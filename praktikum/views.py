from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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
    TugasPendahuluan,
    LaporanMingguan,
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


# ==========================================================
# PUBLIC
# ==========================================================


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

        "kelompok": (
            Kelompok.objects
            .prefetch_related(
                "mentor",
                "peserta"
            )
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

    c["kelompok"] = (
        Kelompok.objects
        .prefetch_related(
            "mentor",
            "peserta"
        )
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

    c["acara"] = (
        Acara.objects
        .prefetch_related("pembawa_acara")
        .all()
    )

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

    for peserta in peserta_data:

        total = Absensi.objects.filter(
            peserta=peserta
        ).count()

        hadir = Absensi.objects.filter(
            peserta=peserta,
            status="H"
        ).count()

        pct = (
            round(hadir / total * 100, 1)
            if total
            else 0
        )

        rows.append({
            "peserta": peserta,
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
        .order_by(
            "urutan",
            "id"
        )
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


def tugas_pendahuluan(request):

    c = context_base()

    c["tugas"] = (
        TugasPendahuluan.objects
        .filter(aktif=True)
        .select_related("acara")
        .order_by("-dibuat")
    )

    return render(
        request,
        "praktikum/tugas_pendahuluan.html",
        c
    )


# ==========================================================
# PESERTA LOGIN
# ==========================================================


def login_peserta(request):

    if request.user.is_authenticated:

        return redirect(
            "dashboard_peserta"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            try:
                peserta = user.profil_peserta

                if not peserta.aktif:

                    messages.error(
                        request,
                        "Akun peserta tidak aktif."
                    )

                    return redirect(
                        "login_peserta"
                    )

            except Peserta.DoesNotExist:

                messages.error(
                    request,
                    "Akun ini belum terhubung dengan data peserta."
                )

                return redirect(
                    "login_peserta"
                )

            login(
                request,
                user
            )

            return redirect(
                "dashboard_peserta"
            )

        messages.error(
            request,
            "Username atau password salah."
        )

    c = context_base()

    return render(
        request,
        "praktikum/login.html",
        c
    )


def logout_peserta(request):

    logout(request)

    return redirect(
        "login_peserta"
    )


# ==========================================================
# DASHBOARD PESERTA
# ==========================================================


@login_required(login_url="/login/")
def dashboard_peserta(request):

    try:

        peserta = (
            Peserta.objects
            .select_related(
                "kelompok"
            )
            .get(akun=request.user)
        )

    except Peserta.DoesNotExist:

        logout(request)

        messages.error(
            request,
            "Profil peserta tidak ditemukan."
        )

        return redirect(
            "login_peserta"
        )

    laporan = (
        LaporanMingguan.objects
        .filter(
            peserta=peserta
        )
        .select_related(
            "acara",
            "kelompok"
        )
    )

    tugas = (
        TugasPendahuluan.objects
        .filter(aktif=True)
        .select_related("acara")
        .order_by("-dibuat")
    )

    c = context_base()

    c.update({

        "peserta": peserta,

        "laporan": laporan,

        "tugas": tugas,

        "acara": Acara.objects.all(),

    })

    return render(
        request,
        "praktikum/dashboard_peserta.html",
        c
    )


# ==========================================================
# UPLOAD LAPORAN
# ==========================================================


@login_required(login_url="/login/")
def upload_laporan(request):

    try:

        peserta = Peserta.objects.get(
            akun=request.user
        )

    except Peserta.DoesNotExist:

        messages.error(
            request,
            "Profil peserta tidak ditemukan."
        )

        return redirect(
            "dashboard_peserta"
        )

    if request.method != "POST":

        return redirect(
            "dashboard_peserta"
        )

    judul = request.POST.get(
        "judul",
        ""
    ).strip()

    acara_id = request.POST.get(
        "acara"
    )

    file = request.FILES.get(
        "file"
    )

    if not judul:

        messages.error(
            request,
            "Judul laporan wajib diisi."
        )

        return redirect(
            "dashboard_peserta"
        )

    if not acara_id:

        messages.error(
            request,
            "Acara wajib dipilih."
        )

        return redirect(
            "dashboard_peserta"
        )

    if not file:

        messages.error(
            request,
            "File laporan wajib diunggah."
        )

        return redirect(
            "dashboard_peserta"
        )

    acara = get_object_or_404(
        Acara,
        id=acara_id
    )

    if not peserta.kelompok:

        messages.error(
            request,
            "Peserta belum memiliki kelompok."
        )

        return redirect(
            "dashboard_peserta"
        )

    LaporanMingguan.objects.create(

        peserta=peserta,

        kelompok=peserta.kelompok,

        acara=acara,

        judul=judul,

        file=file,

        status="menunggu",
    )

    messages.success(
        request,
        "Laporan berhasil diunggah dan menunggu pemeriksaan."
    )

    return redirect(
        "dashboard_peserta"
    )
