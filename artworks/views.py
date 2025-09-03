from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from artworks.models import Artwork, ArtworkImage, Category
from artworks.forms import ArtworkUploadForm
from django.conf import settings

@login_required
def artwork_upload(request):
    # Check if user is an artist
    if request.user.user_type != 'artist':
        messages.error(request, "Only artists can upload artwork")
        return redirect('/')
    
    # DEVELOPMENT MODE - Skip subscription check
    if settings.DEBUG:
        can_upload = True
    else:
        # Production - check subscription
        can_upload = hasattr(request.user, 'subscription') and request.user.subscription.is_active
    
    if not can_upload:
        messages.error(request, "Active subscription required")
        return redirect('subscriptions:plans')
    
    if request.method == 'POST':
        form = ArtworkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user
            artwork.status = 'pending'  # Needs admin approval
            artwork.save()
            
            # Save main image
            if 'main_image' in request.FILES:
                ArtworkImage.objects.create(
                    artwork=artwork,
                    image=request.FILES['main_image'],
                    is_primary=True,
                    order=1
                )
            
            messages.success(request, f'"{artwork.title}" uploaded! Pending admin approval.')
            return redirect('artworks:my_artworks')
    else:
        form = ArtworkUploadForm()
    
    return render(request, 'artworks/upload.html', {'form': form})

@login_required
def my_artworks(request):
    if request.user.user_type != 'artist':
        messages.error(request, "Only artists can view this page")
        return redirect('/')
    
    artworks = Artwork.objects.filter(artist=request.user).order_by('-created_at')
    return render(request, 'artworks/my_artworks.html', {'artworks': artworks})

def gallery(request):
    artworks = Artwork.objects.filter(
        status='active',
        stock_quantity__gt=0
    ).order_by('-created_at')
    return render(request, 'artworks/gallery.html', {'artworks': artworks})

def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    if artwork.status != 'active' and artwork.artist != request.user:
        messages.error(request, "This artwork is not available")
        return redirect('artworks:gallery')
    return render(request, 'artworks/detail.html', {'artwork': artwork})

def home(request):
    # Homepage can show featured artworks
    artworks = Artwork.objects.filter(
        status='active',
        stock_quantity__gt=0
    ).order_by('-created_at')[:6]  # Show 6 latest
    return render(request, 'artworks/home.html', {'artworks': artworks})
