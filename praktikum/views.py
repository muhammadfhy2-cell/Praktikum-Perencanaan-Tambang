from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

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
            .order_by(
                "urutan",
                "tanggal_mulai"
            )[:6]
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
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai"
        )
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

    peserta_data = (
        Peserta.objects
        .filter(aktif=True)
        .select_related("kelompok")
        .prefetch_related("absensi")
        .order_by(
            "kelompok__nama",
            "jabatan",
            "nama"
        )
    )

    rows = []

    for peserta in peserta_data:

        rows.append({
            "peserta": peserta,
            "total_acara": peserta.total_acara_absensi,
            "total_nilai": peserta.total_nilai_absensi,
            "persentase": peserta.persentase_absensi,
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


def login_peserta(request):

    if request.user.is_authenticated:

        try:
            request.user.profil_peserta
            return redirect("dashboard_peserta")
        except Exception:
            pass

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not username or not password:

            messages.error(
                request,
                "Username dan password wajib diisi."
            )

            return render(
                request,
                "praktikum/login.html"
            )

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
                "Akun belum terhubung dengan data peserta "
                "atau peserta tidak aktif."
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


def logout_peserta(request):

    logout(request)

    messages.success(
        request,
        "Anda telah berhasil keluar dari akun."
    )

    return redirect(
        "login_peserta"
    )


@login_required(login_url="/login/")
def dashboard_peserta(request):

    peserta = get_object_or_404(
        Peserta.objects
        .select_related(
            "kelompok",
            "akun"
        ),
        akun=request.user,
        aktif=True,
    )

    tugas = (
        TugasPendahuluan.objects
        .filter(aktif=True)
        .select_related("acara")
        .order_by("-dibuat")
    )

    laporan = (
        LaporanMingguan.objects
        .filter(peserta=peserta)
        .select_related(
            "kelompok",
            "acara"
        )
        .order_by("-uploaded_at")
    )

    total_laporan = laporan.count()

    laporan_acc = laporan.filter(
        status="acc"
    ).count()

    laporan_revisi = laporan.filter(
        status="revisi"
    ).count()

    laporan_menunggu = laporan.filter(
        status="menunggu"
    ).count()

    acara = (
        Acara.objects
        .all()
        .order_by(
            "urutan",
            "tanggal_mulai"
        )
    )

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

        "persentase_absensi": peserta.persentase_absensi,

        "total_acara_absensi": peserta.total_acara_absensi,
    })

    return render(
        request,
        "praktikum/dashboard_peserta.html",
        context
    )


@login_required(login_url="/login/")
def upload_laporan(request):

    peserta = get_object_or_404(
        Peserta.objects
        .select_related(
            "kelompok",
            "akun"
        ),
        akun=request.user,
        aktif=True,
    )

    if request.method != "POST":

        return redirect(
            "dashboard_peserta"
        )

    if not peserta.kelompok:

        messages.error(
            request,
            "Anda belum memiliki kelompok. "
            "Silakan hubungi admin."
        )

        return redirect(
            "dashboard_peserta"
        )

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
            "Acara / minggu wajib dipilih."
        )

        return redirect(
            "dashboard_peserta"
        )

    if not file:

        messages.error(
            request,
            "File laporan wajib diupload."
        )

        return redirect(
            "dashboard_peserta"
        )

    acara = get_object_or_404(
        Acara,
        id=acara_id
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
        "Laporan berhasil dikirim dan "
        "menunggu pemeriksaan admin."
    )

    return redirect(
        "dashboard_peserta"
    )
