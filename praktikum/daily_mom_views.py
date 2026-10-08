from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Acara, DailyMOM, Kelompok, Peserta


def _get_kelompok_login(request):
    """
    Mengambil kelompok yang sedang login berdasarkan session.
    """

    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        return None

    return (
        Kelompok.objects
        .filter(
            id=kelompok_id,
            aktif=True,
        )
        .first()
    )


def _get_ketua_aktif(kelompok):
    """
    Mengambil Ketua aktif dari kelompok.
    """

    return (
        Peserta.objects
        .filter(
            kelompok=kelompok,
            jabatan="ketua",
            aktif=True,
            status_kemajuan="aktif",
        )
        .order_by("nama")
        .first()
    )


def _render_form(
    request,
    kelompok,
    ketua,
    acara_list,
    daily_mom=None,
):
    """
    Menampilkan form tambah/edit DailyMOM.
    """

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


# ============================================================
# TAMBAH DAILY MOM
# ============================================================

def tambah_daily_mom(request):

    # --------------------------------------------------------
    # CEK LOGIN
    # --------------------------------------------------------

    kelompok = _get_kelompok_login(request)

    if not kelompok:
        request.session.pop(
            "kelompok_id",
            None,
        )

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    # --------------------------------------------------------
    # KETUA AKTIF
    # --------------------------------------------------------

    ketua = _get_ketua_aktif(kelompok)

    if not ketua:
        messages.error(
            request,
            "Kelompok belum memiliki Ketua aktif. "
            "DailyMOM tidak dapat dibuat.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # DAFTAR ACARA
    # --------------------------------------------------------

    acara_list = (
        Acara.objects
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    # --------------------------------------------------------
    # FORM
    # --------------------------------------------------------

    if request.method == "POST":

        tanggal = request.POST.get(
            "tanggal",
            "",
        ).strip()

        acara_id = request.POST.get(
            "acara",
            "",
        ).strip()

        judul = request.POST.get(
            "judul",
            "",
        ).strip()

        isi = request.POST.get(
            "isi",
            "",
        ).strip()

        keputusan = request.POST.get(
            "keputusan",
            "",
        ).strip()

        tindak_lanjut = request.POST.get(
            "tindak_lanjut",
            "",
        ).strip()

        # ----------------------------------------------------
        # VALIDASI TANGGAL
        # ----------------------------------------------------

        if not tanggal:
            messages.error(
                request,
                "Tanggal DailyMOM wajib diisi.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
            )

        try:
            tanggal_valid = datetime.strptime(
                tanggal,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            messages.error(
                request,
                "Format tanggal tidak valid.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
            )

        # ----------------------------------------------------
        # VALIDASI ACARA
        # ----------------------------------------------------

        if not acara_id:
            messages.error(
                request,
                "Acara wajib dipilih.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
            )

        acara = (
            Acara.objects
            .filter(
                id=acara_id,
            )
            .first()
        )

        if not acara:
            messages.error(
                request,
                "Acara yang dipilih tidak ditemukan.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
            )

        # ----------------------------------------------------
        # VALIDASI JUDUL
        # ----------------------------------------------------

        if not judul:
            messages.error(
                request,
                "Judul DailyMOM wajib diisi.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
            )

        # ----------------------------------------------------
        # VALIDASI ISI
        # ----------------------------------------------------

        if not isi:
            messages.error(
                request,
                "Isi DailyMOM wajib diisi.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
            )

        # ----------------------------------------------------
        # SIMPAN
        # ----------------------------------------------------

        DailyMOM.objects.create(
            tanggal=tanggal_valid,
            kelompok=kelompok,
            acara=acara,
            judul=judul,
            dibuat_oleh=ketua,
            isi=isi,
            keputusan=keputusan,
            tindak_lanjut=tindak_lanjut,
        )

        messages.success(
            request,
            "DailyMOM berhasil ditambahkan.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # TAMPILKAN FORM
    # --------------------------------------------------------

    return _render_form(
        request,
        kelompok,
        ketua,
        acara_list,
    )


# ============================================================
# EDIT DAILY MOM
# ============================================================

def edit_daily_mom(request, daily_mom_id):

    # --------------------------------------------------------
    # CEK LOGIN
    # --------------------------------------------------------

    kelompok = _get_kelompok_login(request)

    if not kelompok:
        request.session.pop(
            "kelompok_id",
            None,
        )

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    # --------------------------------------------------------
    # KETUA AKTIF
    # --------------------------------------------------------

    ketua = _get_ketua_aktif(kelompok)

    if not ketua:
        messages.error(
            request,
            "Kelompok belum memiliki Ketua aktif.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # AMBIL DAILY MOM MILIK KELOMPOK
    # --------------------------------------------------------

    daily_mom = get_object_or_404(
        DailyMOM.objects.select_related(
            "kelompok",
            "acara",
            "dibuat_oleh",
        ),
        id=daily_mom_id,
        kelompok=kelompok,
    )

    # --------------------------------------------------------
    # DAFTAR ACARA
    # --------------------------------------------------------

    acara_list = (
        Acara.objects
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    # --------------------------------------------------------
    # PROSES UPDATE
    # --------------------------------------------------------

    if request.method == "POST":

        tanggal = request.POST.get(
            "tanggal",
            "",
        ).strip()

        acara_id = request.POST.get(
            "acara",
            "",
        ).strip()

        judul = request.POST.get(
            "judul",
            "",
        ).strip()

        isi = request.POST.get(
            "isi",
            "",
        ).strip()

        keputusan = request.POST.get(
            "keputusan",
            "",
        ).strip()

        tindak_lanjut = request.POST.get(
            "tindak_lanjut",
            "",
        ).strip()

        # ----------------------------------------------------
        # VALIDASI TANGGAL
        # ----------------------------------------------------

        if not tanggal:
            messages.error(
                request,
                "Tanggal DailyMOM wajib diisi.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
                daily_mom,
            )

        try:
            tanggal_valid = datetime.strptime(
                tanggal,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            messages.error(
                request,
                "Format tanggal tidak valid.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
                daily_mom,
            )

        # ----------------------------------------------------
        # VALIDASI ACARA
        # ----------------------------------------------------

        if not acara_id:
            messages.error(
                request,
                "Acara wajib dipilih.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
                daily_mom,
            )

        acara = (
            Acara.objects
            .filter(
                id=acara_id,
            )
            .first()
        )

        if not acara:
            messages.error(
                request,
                "Acara yang dipilih tidak ditemukan.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
                daily_mom,
            )

        # ----------------------------------------------------
        # VALIDASI JUDUL
        # ----------------------------------------------------

        if not judul:
            messages.error(
                request,
                "Judul DailyMOM wajib diisi.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
                daily_mom,
            )

        # ----------------------------------------------------
        # VALIDASI ISI
        # ----------------------------------------------------

        if not isi:
            messages.error(
                request,
                "Isi DailyMOM wajib diisi.",
            )

            return _render_form(
                request,
                kelompok,
                ketua,
                acara_list,
                daily_mom,
            )

        # ----------------------------------------------------
        # UPDATE DATA
        # ----------------------------------------------------

        daily_mom.tanggal = tanggal_valid
        daily_mom.acara = acara
        daily_mom.judul = judul
        daily_mom.isi = isi
        daily_mom.keputusan = keputusan
        daily_mom.tindak_lanjut = tindak_lanjut

        # Tetap mempertahankan Ketua sebagai pembuat
        daily_mom.dibuat_oleh = ketua

        daily_mom.save()

        messages.success(
            request,
            "DailyMOM berhasil diperbarui.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # TAMPILKAN FORM EDIT
    # --------------------------------------------------------

    return _render_form(
        request,
        kelompok,
        ketua,
        acara_list,
        daily_mom,
    )


# ============================================================
# HAPUS DAILY MOM
# ============================================================

def hapus_daily_mom(request, daily_mom_id):

    # --------------------------------------------------------
    # CEK LOGIN
    # --------------------------------------------------------

    kelompok = _get_kelompok_login(request)

    if not kelompok:
        request.session.pop(
            "kelompok_id",
            None,
        )

        messages.warning(
            request,
            "Silakan login terlebih dahulu.",
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    # --------------------------------------------------------
    # KETUA AKTIF
    # --------------------------------------------------------

    ketua = _get_ketua_aktif(kelompok)

    if not ketua:
        messages.error(
            request,
            "Kelompok belum memiliki Ketua aktif.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # HANYA DAILY MOM MILIK KELOMPOK SENDIRI
    # --------------------------------------------------------

    daily_mom = get_object_or_404(
        DailyMOM,
        id=daily_mom_id,
        kelompok=kelompok,
    )

    # --------------------------------------------------------
    # HAPUS HARUS MELALUI POST
    # --------------------------------------------------------

    if request.method != "POST":
        messages.warning(
            request,
            "Penghapusan DailyMOM harus melalui konfirmasi.",
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # --------------------------------------------------------
    # SIMPAN JUDUL UNTUK PESAN
    # --------------------------------------------------------

    judul = daily_mom.judul

    # --------------------------------------------------------
    # HAPUS
    # --------------------------------------------------------

    daily_mom.delete()

    messages.success(
        request,
        f'DailyMOM "{judul}" berhasil dihapus.',
    )

    return redirect(
        "praktikum:dashboard_kelompok"
    )
