from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect, render

from .models import Acara, DailyMOM, Kelompok, Peserta


def tambah_daily_mom(request):
    # ========================================================
    # CEK LOGIN KELOMPOK
    # ========================================================

    kelompok_id = request.session.get("kelompok_id")

    if not kelompok_id:
        messages.warning(
            request,
            "Silakan login terlebih dahulu."
        )
        return redirect(
            "praktikum:login_kelompok"
        )

    # ========================================================
    # AMBIL KELOMPOK AKTIF
    # ========================================================

    kelompok = (
        Kelompok.objects
        .filter(
            id=kelompok_id,
            aktif=True,
        )
        .first()
    )

    if not kelompok:
        request.session.pop(
            "kelompok_id",
            None,
        )

        messages.warning(
            request,
            "Data kelompok tidak ditemukan atau sudah tidak aktif."
        )

        return redirect(
            "praktikum:login_kelompok"
        )

    # ========================================================
    # AMBIL KETUA AKTIF
    # ========================================================

    ketua = (
        Peserta.objects
        .filter(
            kelompok=kelompok,
            jabatan="ketua",
            aktif=True,
            status_kemajuan="aktif",
        )
        .order_by(
            "nama"
        )
        .first()
    )

    # ========================================================
    # JIKA BELUM ADA KETUA
    # ========================================================

    if not ketua:
        messages.error(
            request,
            "Kelompok belum memiliki Ketua aktif. "
            "DailyMOM tidak dapat dibuat."
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # ========================================================
    # DAFTAR ACARA
    # ========================================================

    acara_list = (
        Acara.objects
        .order_by(
            "urutan",
            "tanggal_mulai",
        )
    )

    # ========================================================
    # PROSES POST
    # ========================================================

    if request.method == "POST":

        tanggal = request.POST.get(
            "tanggal",
            ""
        ).strip()

        acara_id = request.POST.get(
            "acara",
            ""
        ).strip()

        judul = request.POST.get(
            "judul",
            ""
        ).strip()

        isi = request.POST.get(
            "isi",
            ""
        ).strip()

        keputusan = request.POST.get(
            "keputusan",
            ""
        ).strip()

        tindak_lanjut = request.POST.get(
            "tindak_lanjut",
            ""
        ).strip()

        # ====================================================
        # VALIDASI TANGGAL
        # ====================================================

        if not tanggal:
            messages.error(
                request,
                "Tanggal DailyMOM wajib diisi."
            )

            return render(
                request,
                "praktikum/daily_mom_tambah.html",
                {
                    "kelompok": kelompok,
                    "ketua": ketua,
                    "acara_list": acara_list,
                },
            )

        try:
            tanggal_valid = datetime.strptime(
                tanggal,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            messages.error(
                request,
                "Format tanggal tidak valid."
            )

            return render(
                request,
                "praktikum/daily_mom_tambah.html",
                {
                    "kelompok": kelompok,
                    "ketua": ketua,
                    "acara_list": acara_list,
                },
            )

        # ====================================================
        # VALIDASI ACARA
        # ====================================================

        if not acara_id:
            messages.error(
                request,
                "Acara wajib dipilih."
            )

            return render(
                request,
                "praktikum/daily_mom_tambah.html",
                {
                    "kelompok": kelompok,
                    "ketua": ketua,
                    "acara_list": acara_list,
                },
            )

        acara = (
            Acara.objects
            .filter(
                id=acara_id
            )
            .first()
        )

        if not acara:
            messages.error(
                request,
                "Acara yang dipilih tidak ditemukan."
            )

            return render(
                request,
                "praktikum/daily_mom_tambah.html",
                {
                    "kelompok": kelompok,
                    "ketua": ketua,
                    "acara_list": acara_list,
                },
            )

        # ====================================================
        # VALIDASI JUDUL
        # ====================================================

        if not judul:
            messages.error(
                request,
                "Judul DailyMOM wajib diisi."
            )

            return render(
                request,
                "praktikum/daily_mom_tambah.html",
                {
                    "kelompok": kelompok,
                    "ketua": ketua,
                    "acara_list": acara_list,
                },
            )

        # ====================================================
        # VALIDASI ISI
        # ====================================================

        if not isi:
            messages.error(
                request,
                "Isi DailyMOM wajib diisi."
            )

            return render(
                request,
                "praktikum/daily_mom_tambah.html",
                {
                    "kelompok": kelompok,
                    "ketua": ketua,
                    "acara_list": acara_list,
                },
            )

        # ====================================================
        # SIMPAN DAILY MOM
        # ====================================================

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

        # ====================================================
        # NOTIFIKASI BERHASIL
        # ====================================================

        messages.success(
            request,
            "DailyMOM berhasil ditambahkan."
        )

        return redirect(
            "praktikum:dashboard_kelompok"
        )

    # ========================================================
    # TAMPILKAN FORM
    # ========================================================

    return render(
        request,
        "praktikum/daily_mom_tambah.html",
        {
            "kelompok": kelompok,
            "ketua": ketua,
            "acara_list": acara_list,
        },
    )
