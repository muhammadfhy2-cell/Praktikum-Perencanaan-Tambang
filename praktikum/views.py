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


# =========================================================
# CONTEXT DASAR WEBSITE
# =========================================================

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


# =========================================================
# HALAMAN PUBLIK
# =========================================================

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
            .all()
            .order_by("urutan", "tanggal_mulai")[:6]
        ),

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

    c["acara"] = (
        Acara.objects
        .all()
        .order_by("urutan", "tanggal_mulai")
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
        .order_by("-uploaded_at")
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
        .order_by("kelompok__nama", "jabatan", "nama")
    )

    for p in peserta_data:

        total = (
            Absensi.objects
            .filter(peserta=p)
            .count()
        )

        hadir = (
            Absensi.objects
            .filter(
                peserta=p,
                status="H"
            )
            .count()
        )

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


# =========================================================
# TUGAS PENDAHULUAN
# =========================================================

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


# =========================================================
# LOGIN PESERTA
# =========================================================

def login_peserta(request):

    # Jika sudah login
    if request.user.is_authenticated:

        try:
            request.user.profil_peserta
            return redirect("dashboard_peserta")

        except Exception:
            pass

    # Proses login
    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # Validasi input
        if not username or not password:

            messages.error(
                request,
                "Username dan password wajib diisi."
            )

            return render(
                request,
                "praktikum/login.html"
            )

        # Autentikasi Django
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            try:
                peserta = user.profil_peserta

            except Exception:
                peserta = None

            # Pastikan user benar-benar terhubung
            # dengan data Peserta
            if peserta and peserta.aktif:

                login(
                    request,
                    user
                )

                return redirect(
                    "dashboard_peserta"
                )

            messages.error(
                request,
                "Akun ini belum terhubung dengan data peserta "
                "atau peserta sedang tidak aktif."
            )

        else:

            messages.error(
                request,
                "Username atau password salah."
            )

    return render(
        request,
        "praktikum/login.html"
    )


# =========================================================
# LOGOUT PESERTA
# =========================================================

def logout_peserta(request):

    logout(request)

    messages.success(
        request,
        "Anda telah berhasil keluar dari akun."
    )

    return redirect(
        "login_peserta"
    )


# =========================================================
# DASHBOARD PESERTA
# =========================================================

@login_required(login_url="/login/")
def dashboard_peserta(request):

    # Ambil profil peserta berdasarkan
    # akun yang sedang login
    peserta = get_object_or_404(
        Peserta.objects.select_related(
            "kelompok",
            "akun"
        ),
        akun=request.user,
        aktif=True,
    )

    # -----------------------------------------------------
    # TUGAS PENDAHULUAN
    # -----------------------------------------------------

    tugas = (
        TugasPendahuluan.objects
        .filter(aktif=True)
        .select_related("acara")
        .order_by("-dibuat")
    )

    # -----------------------------------------------------
    # RIWAYAT LAPORAN PESERTA
    # -----------------------------------------------------

    laporan = (
        LaporanMingguan.objects
        .filter(
            peserta=peserta
        )
        .select_related(
            "kelompok",
            "acara"
        )
        .order_by("-uploaded_at")
    )

    # -----------------------------------------------------
    # STATISTIK LAPORAN
    # -----------------------------------------------------

    total_laporan = laporan.count()

    laporan_acc = (
        laporan
        .filter(status="acc")
        .count()
    )

    laporan_revisi = (
        laporan
        .filter(status="revisi")
        .count()
    )

    laporan_menunggu = (
        laporan
        .filter(status="menunggu")
        .count()
    )

    # -----------------------------------------------------
    # DAFTAR ACARA
    # -----------------------------------------------------

    acara = (
        Acara.objects
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai"
        )
    )

    # -----------------------------------------------------
    # DATA DASHBOARD
    # -----------------------------------------------------

    context = context_base()

    context.update({

        "peserta": peserta,

        "tugas": tugas,

        "laporan": laporan,

        "acara": acara,

        "total_laporan": total_laporan,

        "laporan_acc": laporan_acc,

        "laporan_revisi": laporan_revisi,

        "laporan_menunggu": laporan_menunggu,

    })

    return render(
        request,
        "praktikum/dashboard_peserta.html",
        context
    )


# =========================================================
# UPLOAD LAPORAN MINGGUAN
# =========================================================

@login_required(login_url="/login/")
def upload_laporan(request):

    # Pastikan user memiliki profil peserta
    peserta = get_object_or_404(
        Peserta.objects.select_related(
            "kelompok",
            "akun"
        ),
        akun=request.user,
        aktif=True,
    )

    # Upload hanya melalui POST
    if request.method != "POST":

        return redirect(
            "dashboard_peserta"
        )

    # -----------------------------------------------------
    # CEK KELOMPOK
    # -----------------------------------------------------

    if not peserta.kelompok:

        messages.error(
            request,
            "Anda belum memiliki kelompok. "
            "Silakan hubungi admin praktikum."
        )

        return redirect(
            "dashboard_peserta"
        )

    # -----------------------------------------------------
    # AMBIL DATA FORM
    # -----------------------------------------------------

    judul = request.POST.get(
        "judul",
        ""
    ).strip()

    acara_id = request.POST.get(
        "acara",
        ""
    ).strip()

    file = request.FILES.get(
        "file"
    )

    # -----------------------------------------------------
    # VALIDASI JUDUL
    # -----------------------------------------------------

    if not judul:

        messages.error(
            request,
            "Judul laporan wajib diisi."
        )

        return redirect(
            "dashboard_peserta"
        )

    # -----------------------------------------------------
    # VALIDASI ACARA
    # -----------------------------------------------------

    if not acara_id:

        messages.error(
            request,
            "Acara / minggu wajib dipilih."
        )

        return redirect(
            "dashboard_peserta"
        )

    # -----------------------------------------------------
    # VALIDASI FILE
    # -----------------------------------------------------

    if not file:

        messages.error(
            request,
            "File laporan wajib diupload."
        )

        return redirect(
            "dashboard_peserta"
        )

    # -----------------------------------------------------
    # AMBIL ACARA
    # -----------------------------------------------------

    acara = get_object_or_404(
        Acara,
        id=acara_id
    )

    # -----------------------------------------------------
    # SIMPAN LAPORAN
    # -----------------------------------------------------

    LaporanMingguan.objects.create(

        peserta=peserta,

        # Kelompok otomatis mengambil
        # dari profil peserta
        kelompok=peserta.kelompok,

        acara=acara,

        judul=judul,

        file=file,

        # Semua upload baru masuk
        # sebagai Menunggu Pemeriksaan
        status="menunggu",
    )

    # -----------------------------------------------------
    # PESAN BERHASIL
    # -----------------------------------------------------

    messages.success(
        request,
        "Laporan berhasil diupload dan "
        "menunggu pemeriksaan admin."
    )

    return redirect(
        "dashboard_peserta"
    )
