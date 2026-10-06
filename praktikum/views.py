from django.shortcuts import render

from .models import (
    Setting,
    Staff,
    Kelompok,
    Peserta,
    Acara,
    Materi,
    Absensi,
    Pengumuman,
    TataTertib,
)


def context_base():
    setting = Setting.objects.first()

    return {
        "setting": setting or Setting(
            nama_praktikum="Praktikum Perencanaan Tambang"
        ),

        "penanggung_jawab": Staff.objects.filter(
            jabatan="penanggung_jawab",
            aktif=True
        ),

        "koordinator": Staff.objects.filter(
            jabatan="koordinator",
            aktif=True
        ),

        "asisten": Staff.objects.filter(
            jabatan="asisten",
            aktif=True
        ),
    }


def home(request):
    c = context_base()

    c.update({
        "pengumuman": (
            Pengumuman.objects
            .filter(aktif=True)
            .order_by("-dibuat")[:5]
        ),

        "acara": (
            Acara.objects
            .all()[:6]
        ),

        # PERBAIKAN:
        # mentor adalah ManyToManyField,
        # sehingga harus menggunakan prefetch_related
        "kelompok": (
            Kelompok.objects
            .prefetch_related("mentor", "peserta")
            .all()
        ),

        "materi": (
            Materi.objects
            .select_related("acara")
            .all()[:5]
        ),
    })

    return render(
        request,
        "praktikum/home.html",
        c
    )


def kelompok(request):
    c = context_base()

    # PERBAIKAN:
    # select_related("mentor") -> prefetch_related("mentor")
    c["kelompok"] = (
        Kelompok.objects
        .prefetch_related("mentor", "peserta")
        .all()
    )

    return render(
        request,
        "praktikum/kelompok.html",
        c
    )


def personel(request):
    c = context_base()

    return render(
        request,
        "praktikum/personel.html",
        c
    )


def jadwal(request):
    c = context_base()

    c["acara"] = Acara.objects.all()

    return render(
        request,
        "praktikum/jadwal.html",
        c
    )


def materi(request):
    c = context_base()

    c["materi"] = (
        Materi.objects
        .select_related("acara")
        .all()
    )

    return render(
        request,
        "praktikum/materi.html",
        c
    )


def absensi(request):
    c = context_base()

    rows = []

    peserta_data = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
    )

    for p in peserta_data:

        total = Absensi.objects.filter(
            peserta=p
        ).count()

        hadir = Absensi.objects.filter(
            peserta=p,
            status="H"
        ).count()

        pct = (
            round(hadir / total * 100, 1)
            if total
            else 0
        )

        rows.append({
            "peserta": p,
            "total": total,
            "hadir": hadir,
            "pct": pct,
        })

    c["rows"] = rows

    return render(
        request,
        "praktikum/absensi.html",
        c
    )


def tata_tertib(request):
    c = context_base()

    c["items"] = (
        TataTertib.objects
        .filter(aktif=True)
        .order_by("urutan", "id")
    )

    return render(
        request,
        "praktikum/tata_tertib.html",
        c
    )


def pengumuman(request):
    c = context_base()

    c["items"] = (
        Pengumuman.objects
        .filter(aktif=True)
        .order_by("-dibuat")
    )

    return render(
        request,
        "praktikum/pengumuman.html",
        c
    )
