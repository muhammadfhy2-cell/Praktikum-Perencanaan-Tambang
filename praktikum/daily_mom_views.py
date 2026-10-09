from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Acara, DailyMOM, Kelompok, Peserta


def _get_kelompok_login(request):
    """Mengambil kelompok aktif berdasarkan session login."""

    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        return None

    return Kelompok.objects.filter(
        id=kelompok_id,
        aktif=True,
    ).first()


def _get_ketua_aktif(kelompok):
    """Mengambil Ketua yang masih aktif pada kelompok."""

    return (
        Peserta.objects.filter(
            kelompok=kelompok,
            jabatan="ketua",
            aktif=True,
            status_kemajuan="aktif",
        )
        .order_by("nama")
        .first()
    )


def _get_acara_list():
    """Mengambil daftar acara untuk formulir Daily MOM."""

    return Acara.objects.order_by("urutan", "tanggal_mulai")


def _render_form(request, kelompok, ketua, acara_list, daily_mom=None):
    """Menampilkan formulir tambah atau edit Daily MOM."""

    return render(
        request,
        "praktikum/daily_mom_tambah.html",
        {
            "kelompok": kelompok,
            "ketua": ketua,
            "acara_list": acara_list,
            "daily_mom": daily_mom,
            "mode_edit": daily_mom is not None,
        },
    )


def _validasi_form(request, kelompok, ketua, acara_list, daily_mom=None):
    """Memvalidasi masukan formulir dan mengembalikan data yang valid."""

    tanggal = request.POST.get("tanggal", "").strip()
    acara_id = request.POST.get("acara", "").strip()
    judul = request.POST.get("judul", "").strip()
    isi = request.POST.get("isi", "").strip()
    keputusan = request.POST.get("keputusan", "").strip()
    tindak_lanjut = request.POST.get("tindak_lanjut", "").strip()

    if not tanggal:
        messages.error(request, "Tanggal Daily MOM wajib diisi.")
        return None

    try:
        tanggal_valid = datetime.strptime(tanggal, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Format tanggal tidak valid.")
        return None

    if not acara_id:
        messages.error(request, "Acara wajib dipilih.")
        return None

    acara = Acara.objects.filter(id=acara_id).first()

    if not acara:
        messages.error(request, "Acara yang dipilih tidak ditemukan.")
        return None

    if not judul:
        messages.error(request, "Judul Daily MOM wajib diisi.")
        return None

    if not isi:
        messages.error(request, "Isi Daily MOM wajib diisi.")
        return None

    return {
        "tanggal": tanggal_valid,
        "acara": acara,
        "judul": judul,
        "isi": isi,
        "keputusan": keputusan,
        "tindak_lanjut": tindak_lanjut,
    }


def tambah_daily_mom(request):
    """Membuat Daily MOM baru untuk kelompok yang sedang login."""

    kelompok = _get_kelompok_login(request)

    if not kelompok:
        request.session.pop("kelompok_id", None)
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    ketua = _get_ketua_aktif(kelompok)

    if not ketua:
        messages.error(
            request,
            "Kelompok belum memiliki Ketua aktif. Daily MOM tidak dapat dibuat.",
        )
        return redirect("praktikum:dashboard_kelompok")

    acara_list = _get_acara_list()

    if request.method == "POST":
        data = _validasi_form(
            request,
            kelompok,
            ketua,
            acara_list,
        )

        if data is None:
            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
            )

        DailyMOM.objects.create(
            kelompok=kelompok,
            dibuat_oleh=ketua,
            **data,
        )

        messages.success(request, "Daily MOM berhasil ditambahkan.")
        return redirect("praktikum:dashboard_kelompok")

    return _render_form(request, kelompok, ketua, acara_list)


def edit_daily_mom(request, daily_mom_id):
    """Mengedit Daily MOM yang dimiliki kelompok yang sedang login."""

    kelompok = _get_kelompok_login(request)

    if not kelompok:
        request.session.pop("kelompok_id", None)
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    ketua = _get_ketua_aktif(kelompok)

    if not ketua:
        messages.error(request, "Kelompok belum memiliki Ketua aktif.")
        return redirect("praktikum:dashboard_kelompok")

    daily_mom = get_object_or_404(
        DailyMOM.objects.select_related(
            "kelompok",
            "acara",
            "dibuat_oleh",
        ),
        id=daily_mom_id,
        kelompok=kelompok,
    )

    acara_list = _get_acara_list()

    if request.method == "POST":
        data = _validasi_form(
            request,
            kelompok,
            ketua,
            acara_list,
            daily_mom,
        )

        if data is None:
            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
                daily_mom,
            )

        daily_mom.tanggal = data["tanggal"]
        daily_mom.acara = data["acara"]
        daily_mom.judul = data["judul"]
        daily_mom.isi = data["isi"]
        daily_mom.keputusan = data["keputusan"]
        daily_mom.tindak_lanjut = data["tindak_lanjut"]

        # Pertahankan pembuat asli agar riwayat kepengarangan tidak berubah.
        daily_mom.save()

        messages.success(request, "Daily MOM berhasil diperbarui.")
        return redirect("praktikum:dashboard_kelompok")

    return _render_form(
        request,
        kelompok,
        ketua,
        acara_list,
        daily_mom,
    )


@require_POST
def hapus_daily_mom(request, daily_mom_id):
    """Menghapus Daily MOM milik kelompok melalui permintaan POST saja."""

    kelompok = _get_kelompok_login(request)

    if not kelompok:
        request.session.pop("kelompok_id", None)
        messages.warning(request, "Silakan login terlebih dahulu.")
        return redirect("praktikum:login_kelompok")

    ketua = _get_ketua_aktif(kelompok)

    if not ketua:
        messages.error(request, "Kelompok belum memiliki Ketua aktif.")
        return redirect("praktikum:dashboard_kelompok")

    daily_mom = get_object_or_404(
        DailyMOM,
        id=daily_mom_id,
        kelompok=kelompok,
    )

    judul = daily_mom.judul
    daily_mom.delete()

    messages.success(
        request,
        f'Daily MOM "{judul}" berhasil dihapus.',
    )

    return redirect("praktikum:dashboard_kelompok")
