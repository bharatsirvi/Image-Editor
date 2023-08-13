from django.shortcuts import render,redirect
from django.contrib import messages
from .models import ImageFile
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import cv2
import os
from django.http import FileResponse
import mimetypes
from PIL import Image, ImageEnhance
import io
from django.views.decorators.csrf import csrf_exempt
import base64
import tempfile
import shutil
from PIL import Image, JpegImagePlugin
import numpy as np
import json

def remove_old_files(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
            
def index(request,methods=["POST",'GET']):
    remove_old_files('static/processed')
    remove_old_files('static/upload')
    remove_old_files('static/compressed')
    remove_old_files('static/filtered')
    ImageFile.objects.all().delete()    
    if request.method=='POST':
        if len(request.FILES)!=0:
            img_file = request.FILES['in-image']
            image_obj = ImageFile(img=img_file)
            image_obj.save()
            return redirect('/home')
        else:
            ImageFile.objects.all().delete()
            return redirect('/') 
    return render(request,"index.html")

def home(request):
    if ImageFile.objects.exists():
        last_object = ImageFile.objects.latest('created_at')
        objs_to_delete = ImageFile.objects.exclude(pk=last_object.pk).order_by('-created_at')
        objs_to_delete.delete()
        if last_object.filtered_img:
            last_object.filtered_img.delete()
        if request.session.get('data'):
            data_received = request.session.get('data') 
        else:
            data_received=False                  
        context={
        "type":data_received,
        'resize_apply':False,
        'obj': last_object
        }  
        return render(request,"home.html",context)
    return redirect('/')



def crop(request):
    temp=None;
    if ImageFile.objects.exists():   
        last_object = ImageFile.objects.latest('created_at')
        # if last_object.processed_img:
        #     temp= cv2.imread(last_object.processed_img.path)
        # else:
        #     temp=cv2.imread(last_object.img.path) 
            
        # request.session['temp'] = temp                     
        context={
        'obj': last_object
        }
        return render(request,"crop.html",context)    
    return redirect('/')
def crop_reset(request,methods=["POST"]):
    # temp = request.session.get('temp')
    if request.method=='POST':
        if 'crop-button' in request.POST: 
            width = int(request.POST.get('cwidth'))
            height = int(request.POST.get('cheight'))
            position_x = int(request.POST.get('position-x'))
            position_y =int(request.POST.get('position-y'))
            last_object = ImageFile.objects.latest ('created_at')
            if last_object.processed_img :
                processed_img_path = last_object.processed_img.path
                proimg = cv2.imread(processed_img_path)
                x1, y1 = position_x, position_y
                x2, y2 = position_x + width, position_y + height
                processed_img = proimg[y1:y2,x1:x2]
            else:
                original_img_path = last_object.img.path
                img = cv2.imread(original_img_path)
                x1, y1 = position_x, position_y
                x2, y2 = position_x + width, position_y + height
                processed_img =img[y1:y2, x1:x2] 
            processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', 'processed_image.png')
            cv2.imwrite(processed_img_path, processed_img)
            with open(processed_img_path, 'rb') as f:
                last_object.processed_img.save('processed_image.png', ContentFile(f.read()), save=True) 
            return redirect('/crop')
        
        # elif 'reset-button' in request.POST:
        #     last_object = ImageFile.objects.latest('created_at')
        #     processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', 'processed_image.png')
        #     # cv2.imwrite(processed_img_path, temp)
        #     with open(processed_img_path, 'rb') as f:
        #             last_object.processed_img.save('processed_image.png', ContentFile(f.read()), save=True)
        #     del request.session['temp']        
        #     return redirect('/crop')
    return redirect("/crop")  
        
def flip(request):
    if ImageFile.objects.exists():
        last_object = ImageFile.objects.latest('created_at')
        context={
        'obj': last_object
        }
        return render(request,"flip.html",context)    
    return redirect('/')

def dimensions(request): 
    if ImageFile.objects.exists():
        data_to_pass =True
        request.session['data'] = data_to_pass
        # context={
        # 'obj': last_object,
        # "type":True,
        # }
        return redirect('/home')    
    return redirect('/')

def percentage(request):
    if ImageFile.objects.exists():
        data_to_pass =False
        request.session['data'] = data_to_pass
        # context={
        # 'obj': last_object,
        # "type":True,
        # }
        return redirect('/home')   
    return redirect('/')

def fliprotate(request,methods=['GET','POST']):
    if request.method == 'POST':
        if 'flip_horizontal' in request.POST:        
            last_object = ImageFile.objects.latest('created_at')
            if last_object.processed_img :
                processed_img_path = last_object.processed_img.path
                proimg = cv2.imread(processed_img_path)
                processed_img = cv2.flip(proimg, 1) 
            else:
                original_img_path = last_object.img.path
                img = cv2.imread(original_img_path)
                processed_img = cv2.flip(img, 1) 
                          
            processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', 'processed_image.png')
            cv2.imwrite(processed_img_path, processed_img)
            with open(processed_img_path, 'rb') as f:
                last_object.processed_img.save('processed_image.png', ContentFile(f.read()), save=True)                
            redirect('/flip')
          
        elif 'flip_vertical' in request.POST:
            last_object = ImageFile.objects.latest('created_at')
            if last_object.processed_img :
                processed_img_path = last_object.processed_img.path
                proimg = cv2.imread(processed_img_path)
                processed_img = cv2.flip(proimg, 0) 
            else:
                original_img_path = last_object.img.path
                img = cv2.imread(original_img_path)
                processed_img = cv2.flip(img, 0) 
                          
            processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', 'processed_image.png')
            cv2.imwrite(processed_img_path, processed_img)
            with open(processed_img_path, 'rb') as f:
                last_object.processed_img.save('processed_image.png', ContentFile(f.read()), save=True)
            redirect('/flip')  
    

        elif 'rotate_clockwise' in request.POST:
            last_object = ImageFile.objects.latest('created_at')
            if last_object.processed_img :
                processed_img_path = last_object.processed_img.path
                proimg = cv2.imread(processed_img_path)
                processed_img = cv2.rotate(proimg, cv2.ROTATE_90_CLOCKWISE) 
            else:
                original_img_path = last_object.img.path
                img = cv2.imread(original_img_path)
                processed_img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) 
                          
            processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', 'processed_image.png')
            cv2.imwrite(processed_img_path, processed_img)
            with open(processed_img_path, 'rb') as f:
                last_object.processed_img.save('processed_image.png', ContentFile(f.read()), save=True)
            redirect('/flip')
        
        elif 'rotate_anticlockwise' in request.POST:
            last_object = ImageFile.objects.latest('created_at')
            if last_object.processed_img :
                processed_img_path = last_object.processed_img.path
                proimg = cv2.imread(processed_img_path)
                processed_img = cv2.rotate(proimg, cv2.ROTATE_90_COUNTERCLOCKWISE) 
            else:
                original_img_path = last_object.img.path
                img = cv2.imread(original_img_path)
                processed_img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE) 
                          
            processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', 'processed_image.png')
            cv2.imwrite(processed_img_path, processed_img)
            with open(processed_img_path, 'rb') as f:
                last_object.processed_img.save('processed_image.png', ContentFile(f.read()), save=True)
            redirect('/flip')
            
    return redirect('/flip')
    
def contact(request):
    last_object = ImageFile.objects.latest('created_at') 
    if last_object.filtered_img:
            last_object.filtered_img.delete()
    return render(request,"contact.html")

def about(request):
    last_object = ImageFile.objects.latest('created_at') 
    if last_object.filtered_img:
            last_object.filtered_img.delete()
    return render(request,"about.html")

def services(request):
    return render(request,"services.html")

def resize(request,mehods=["POST"]):
    if request.method == 'POST':
        Type = request.POST.get('type','')
        width = int(request.POST.get('width', 0))
        height = int(request.POST.get('height', 0))
        file_format = request.POST.get('format')
        print('file_format'+ file_format)
        size_percentage = int(request.POST.get('size-per', 0))
        unit = request.POST.get('unit', '')  # 'pixel', 'inch', 'cm', 'mm'
        last_object = ImageFile.objects.latest('created_at')
        original_extension = os.path.splitext(os.path.basename(last_object.img.name))[1]
        file_extension = original_extension if file_format == 'original' else '.' + file_format     
        new_processed_img_name = os.path.splitext(os.path.basename(last_object.img.name))[0] + '_new' + file_extension     
        print(new_processed_img_name)
                  
        if last_object.processed_img:
            processed_img_path = last_object.processed_img.path
            proimg = cv2.imread(processed_img_path)
            conversion_factors = {
                'pixel': 1,
                'inch': 96,  # 1 inch = 96 pixels (assuming standard screen resolution)
                'cm': 37.8,  # 1 cm = 37.8 pixels (assuming standard screen resolution)
                'mm': 3.78,  # 1 mm = 3.78 pixels (assuming standard screen resolution)
            }

            if unit in conversion_factors:
                width_pixels = int(width * conversion_factors[unit])
                height_pixels = int(height * conversion_factors[unit])
            else:
                # If the unit is not recognized, default to pixels
                width_pixels = width
                height_pixels = height
            # Perform resizing based on the selected option
            if Type == 'dimensions':
                processed_img = cv2.resize(proimg, (width_pixels, height_pixels))
                processed_img_path =  os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name) 
                cv2.imwrite(processed_img_path, processed_img)
                with open(processed_img_path, 'rb') as f:
                    last_object.processed_img.save('processed_img.png', ContentFile(f.read()), save=True) 
                # new_processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name)      
                content_type, _ = mimetypes.guess_type(processed_img_path)
                response = FileResponse(open(processed_img_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{new_processed_img_name}"'
                return response  
            elif Type == 'percentage':
                processed_img = cv2.resize(proimg, (0, 0), fx= size_percentage / 100, fy=size_percentage / 100)
                processed_img_path =  os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name) 
                cv2.imwrite(processed_img_path, processed_img)
                with open('processed_img.png', 'rb') as f:
                    last_object.processed_img.save(new_processed_img_name, ContentFile(f.read()), save=True) 
                # new_processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name)      
                content_type, _ = mimetypes.guess_type(processed_img_path)
                response = FileResponse(open(processed_img_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{new_processed_img_name}"'
                return response 
        else:
            original_img_path = last_object.img.path
            img = cv2.imread(original_img_path)
            conversion_factors = {
                'pixel': 1,
                'inch': 96,  # 1 inch = 96 pixels (assuming standard screen resolution)
                'cm': 37.8,  # 1 cm = 37.8 pixels (assuming standard screen resolution)
                'mm': 3.78,  # 1 mm = 3.78 pixels (assuming standard screen resolution)
            }

            if unit in conversion_factors:
                width_pixels = int(width * conversion_factors[unit])
                height_pixels = int(height * conversion_factors[unit])
            else:
                # If the unit is not recognized, default to pixels
                width_pixels = width
                height_pixels = height
            # Perform resizing based on the selected option
            if Type == 'dimensions':
                processed_img = cv2.resize(img, (width_pixels, height_pixels))
                processed_img_path =  os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name) 
                cv2.imwrite(processed_img_path, processed_img)
                with open(processed_img_path, 'rb') as f:
                    last_object.processed_img.save('processed_img.png', ContentFile(f.read()), save=True) 
                # new_processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name)      
                content_type, _ = mimetypes.guess_type(processed_img_path)
                response = FileResponse(open(processed_img_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{new_processed_img_name}"'
                return response 
            elif Type == 'percentage':
                processed_img = cv2.resize(img, (0, 0), fx= size_percentage / 100, fy=size_percentage / 100)
                processed_img_path =  os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name) 
                cv2.imwrite(processed_img_path, processed_img)
                with open(processed_img_path, 'rb') as f:
                    last_object.processed_img.save('processed_img.png', ContentFile(f.read()), save=True) 
                # new_processed_img_path = os.path.join(settings.MEDIA_ROOT, 'processed', new_processed_img_name)      
                content_type, _ = mimetypes.guess_type(processed_img_path)
                response = FileResponse(open(processed_img_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{new_processed_img_name}"'
                return response
        if request.session.get('data'):
            data_received = request.session.get('data') 
        else:
            data_received=False        
        context={
        "type":data_received,
        'resize_apply':True,
        'obj': last_object
        }  
        return render(request,"home.html",context)

    return render(request, '/')
        
def reset (request):
    processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
    last_object = ImageFile.objects.latest('created_at')
    last_object.processed_img = None
    last_object.compressed_img = None
    last_object.filtered_img=None
    last_object.save()
    #         file_path =last_object.compressed_img.path
    #         try:
    #             os.remove(file_path)            
    #             last_object.compressed_img = None
    #             last_object.save()
    #             print(f"File '{file_path}' deleted successfully.")
    #         except Exception as e:
    #             print(f"An error occurred: {e}")  
                
    return redirect(request.META.get('HTTP_REFERER'))

def reupload(request,methods=['POST']):
    return redirect('/')

def compressor(request):
    if ImageFile.objects.exists():
        quality_percentage = 100
        last_object = ImageFile.objects.latest('created_at') 
        if last_object.filtered_img:
            last_object.filtered_img.delete()   
        
        if  last_object.processed_img:
            new_processed_img_name = os.path.basename(last_object.processed_img.name)
            compressed_img_copy = create_compressed_copy(last_object.processed_img, quality_percentage)
            last_object.compressed_img.save(new_processed_img_name, ContentFile(compressed_img_copy.getvalue()), save=True)
            compressed_img_size = int(len(last_object.compressed_img.read()) / 1024)  #
          
            return render(request, 'compressor.html', {'obj': last_object,'size':compressed_img_size})
        else:
            new_processed_img_name = os.path.basename(last_object.img.name)
            compressed_img_copy = create_compressed_copy(last_object.img, quality_percentage)
             
            last_object.compressed_img.save(new_processed_img_name, ContentFile(compressed_img_copy.getvalue()), save=True)
            compressed_img_size = int(len(last_object.compressed_img.read()) / 1024 )  # Size in KB        
            return render(request, 'compressor.html', {'obj': last_object,'size':compressed_img_size})
    return redirect('/compressor')

def compress(request,methods=['POST']):
    if request.method == 'POST':
        
        quality_percentage = int(request.POST.get('quality', 100))
        last_object = ImageFile.objects.latest('created_at')
        file_format = request.POST.get('format')
        original_extension = os.path.splitext(os.path.basename(last_object.img.name))[1]
        file_extension = original_extension if file_format == 'original' else '.' + file_format     
        new_processed_img_name = os.path.splitext(os.path.basename(last_object.img.name))[0] + '_compress' + file_extension
        
        if last_object.processed_img:
            compressed_img_copy = create_compressed_copy(last_object.processed_img, quality_percentage)
        
        # Save the compressed image data to the compressed_img field of the model
            last_object.compressed_img.save(new_processed_img_name, ContentFile(compressed_img_copy.getvalue()), save=True)
            compressed_img_size = int(len(last_object.compressed_img.read()) / 1024 ) #
            messages.success(request, "Successfully ! Your Image Compressed" )
            return render(request, 'compressor.html', {'obj': last_object,'size':compressed_img_size})
        else:
            compressed_img_copy = create_compressed_copy(last_object.img, quality_percentage)
        
        # Save the compressed image data to the compressed_img field of the model
            last_object.compressed_img.save(new_processed_img_name, ContentFile(compressed_img_copy.getvalue()), save=True)
            compressed_img_size = int(len(last_object.compressed_img.read()) / 1024 )  # Size in KB
            messages.success(request, "Successfully ! Your Image Compressed" )
            return render(request, 'compressor.html', {'obj': last_object,'size':compressed_img_size})
    return redirect('/compressor')


def create_compressed_copy(image_obj, quality_percentage):
    image = Image.open(image_obj)
    
    # Convert image to RGB mode if it's not already in that mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Create an output buffer to store the compressed image
    output = io.BytesIO()
    
    # Save the image with lossless optimization
    image.save(output, format='JPEG', quality=quality_percentage-20, optimize=True)
    
    return output
        
def down_compress(request,methods=['POST']):
    if request.method=="POST":
        if 'download' in request.POST:   
            last_object = ImageFile.objects.latest('created_at')
            if last_object.compressed_img:
                compressed_img_path = last_object.compressed_img.path
                
                # Set the appropriate content type for the response
                content_type, _ = mimetypes.guess_type(compressed_img_path)
                response = FileResponse(open(compressed_img_path, 'rb'), content_type=content_type)
                
                # Set the Content-Disposition header for download
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(compressed_img_path)}"'
                return response      
        else:
            last_object = ImageFile.objects.latest('created_at')
            last_object.compressed_img=None
            return redirect('/compressor')   
 
def down_filter(request,methods=["post"]):
    if request.method=="POST":
        if 'download' in request.POST:   
            last_object = ImageFile.objects.latest('created_at')
            if last_object.filtered_img:
                filtered_img_path = last_object.filtered_img.path
                
                # Set the appropriate content type for the response
                content_type, _ = mimetypes.guess_type(filtered_img_path)
                response = FileResponse(open(filtered_img_path, 'rb'), content_type=content_type)
                
                # Set the Content-Disposition header for download
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filtered_img_path)}"'
                return response      
        else:
            last_object = ImageFile.objects.latest('created_at')
            last_object.filtered_img.delete()
            return redirect('/filter')    

def down_resize(request,methods=["post"]):
    if request.method=="POST":
        if 'download' in request.POST:   
            last_object = ImageFile.objects.latest('created_at')
            if last_object.processed_img:
                processed_img_path = last_object.processed_img.path
                content_type, _ = mimetypes.guess_type(processed_img_path)
                response = FileResponse(open(processed_img_path, 'rb'), content_type=content_type)
                
                # Set the Content-Disposition header for download
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(processed_img_path)}"'
                return response      
        else:
            last_object = ImageFile.objects.latest('created_at')
            last_object.processed_img.delete()
            return redirect('/home')          
           
def adjust(request):
    if ImageFile.objects.exists():
        last_object = ImageFile.objects.latest('created_at')
        if last_object.filtered_img:
            last_object.filtered_img.delete()   
        context={
        'obj': last_object
        } 
        return render(request,'adjust.html',context)    
def filter (request):
    if ImageFile.objects.exists():
        last_object = ImageFile.objects.latest('created_at')
        context={
         'filter_apply':False,   
        'obj': last_object
        } 
        return render(request,'filter.html',context)


def apply_filter(request,methods=["POST"]):
    if request.method == 'POST':
        last_object = ImageFile.objects.latest('created_at')  
        filter_type = request.POST.get('filter_type') 
        file_format = request.POST.get('format') 
        original_extension = os.path.splitext(os.path.basename(last_object.img.name))[1]
        file_extension = original_extension if file_format == 'original' else '.' + file_format     
        new_filtered_img_name = os.path.splitext(os.path.basename(last_object.img.name))[0] + '_new' + file_extension
        
        if 'apply-filter' in request.POST:
            if last_object.filtered_img:
                filtered_img_path = last_object.filtered_img.path
                content_type, _ = mimetypes.guess_type(filtered_img_path)
                response = FileResponse(open(filtered_img_path, 'rb'), content_type=content_type)
                
                response['Content-Disposition'] = response['Content-Disposition'] = f'attachment; filename="{new_filtered_img_name}"'
                return response                
            return redirect('/filter')
        
        elif 'remove-filter' in request.POST:
            last_object = ImageFile.objects.latest('created_at')
            last_object.filtered_img.delete()
            return redirect('/filter')    
            
                
        if last_object.processed_img:
            img_path = last_object.processed_img.path
            img = cv2.imread(img_path)
            
            if filter_type == 'vintage':
                filtered_img = apply_vintage_effect(img)
            elif filter_type == 'cool':
                filtered_img = apply_cool_effect(img)
            elif filter_type == 'warm':
                filtered_img = apply_warm_effect(img)
            elif filter_type == 'sepia':
                filtered_img = apply_sepia_effect(img)
            elif filter_type == 'grayscale':
                filtered_img = apply_grayscale_effect(img)
            elif filter_type == 'sketch':
                filtered_img = apply_sketch_effect(img)    
            elif filter_type == 'dreamy':
                filtered_img = apply_dreamy_effect(img)   
            elif filter_type == 'amaro':
                filtered_img = apply_amaro_effect(img)   
            elif filter_type == 'lark':
                filtered_img = apply_beauty_filter(img)
            elif filter_type == 'clarendon':
                filtered_img = apply_valencia_filter(img) 
            elif filter_type == 'juno':
                filtered_img = apply_juno_filter(img)        
            elif filter_type == 'xpro_ii':
                filtered_img = apply_xpro_ii_effect(img) 
            elif filter_type == 'vsco':
                filtered_img = apply_vsco_filter(img)                     
            elif filter_type == 'sunned_up':
                filtered_img = apply_sunned_up_effect(img)     
            elif filter_type == 'invert':
                filtered_img = apply_invert_effect(img) 
            elif filter_type == 'emboss':
                filtered_img = apply_emboss_effect(img) 
            elif filter_type == 'gradient':
                filtered_img = apply_gradient_map(img)
            elif filter_type == 'light_sepia':
                filtered_img = apply_light_sepia_effect(img)
            elif filter_type == 'magenta':
                filtered_img = apply_magenta_haze_effect(img)
            elif filter_type == 'tea':
                filtered_img =  apply_tea_filter(img)
            elif filter_type == 'sunny':
                filtered_img =  apply_sunny_effect(img)
                                
            target_dir = 'static/filtered/'
            os.makedirs(target_dir, exist_ok=True)
            filtered_img_path = os.path.join(settings.MEDIA_ROOT, 'filtered', new_filtered_img_name)
            cv2.imwrite(filtered_img_path,filtered_img)              
            with open(filtered_img_path, 'rb') as f:
                last_object.filtered_img.save(new_filtered_img_name, ContentFile(f.read()), save=True)
                
        elif last_object.img:
            img_path = last_object.img.path
            img = cv2.imread(img_path)
            if filter_type == 'vintage':
                filtered_img = apply_vintage_effect(img)
            elif filter_type == 'cool':
                filtered_img = apply_cool_effect(img)
            elif filter_type == 'warm':
                filtered_img = apply_warm_effect(img)
            elif filter_type == 'sepia':
                filtered_img = apply_sepia_effect(img)
            elif filter_type == 'grayscale':
                filtered_img = apply_grayscale_effect(img)
            elif filter_type == 'sketch':
                filtered_img = apply_sketch_effect(img)    
            elif filter_type == 'dreamy':
                filtered_img = apply_dreamy_effect(img)   
            elif filter_type == 'amaro':
                filtered_img = apply_amaro_effect(img)   
            elif filter_type == 'lark':
                filtered_img = apply_beauty_filter(img)
            elif filter_type == 'clarendon':
                filtered_img = apply_valencia_filter(img) 
            elif filter_type == 'juno':
                filtered_img = apply_juno_filter(img)        
            elif filter_type == 'xpro_ii':
                filtered_img = apply_xpro_ii_effect(img) 
            elif filter_type == 'vsco':
                filtered_img = apply_vsco_filter(img)                     
            elif filter_type == 'sunned_up':
                filtered_img = apply_sunned_up_effect(img)     
            elif filter_type == 'invert':
                filtered_img = apply_invert_effect(img) 
            elif filter_type == 'emboss':
                filtered_img = apply_emboss_effect(img) 
            elif filter_type == 'gradient':
                filtered_img = apply_gradient_map(img)
            elif filter_type == 'light_sepia':
                filtered_img = apply_light_sepia_effect(img)
            elif filter_type == 'magenta':
                filtered_img = apply_magenta_haze_effect(img)
            elif filter_type == 'tea':
                filtered_img =  apply_tea_filter(img)
            elif filter_type == 'sunny':
                filtered_img =  apply_sunny_effect(img)
                                
            target_dir = 'static/filtered/'
            os.makedirs(target_dir, exist_ok=True)
            filtered_img_path = os.path.join(settings.MEDIA_ROOT, 'filtered', new_filtered_img_name)
            cv2.imwrite(filtered_img_path,filtered_img)               
            with open(filtered_img_path, 'rb') as f:
                last_object.filtered_img.save(new_filtered_img_name, ContentFile(f.read()), save=True)
                             
        return redirect('/filter')  
    return redirect('/filter')    
  
def apply_cool_effect(image):
    # Increase blue channel and decrease red channel
    blue, green, red = cv2.split(image)

    blue = cv2.addWeighted(blue, 1.2, 0, 0, 0)
    red = cv2.addWeighted(red, 0.7, 0, 0, 0)

    cool_effect_img = cv2.merge((blue, green, red))

    return cool_effect_img

def apply_invert_effect(image):
    inverted_image = 255 - image
    return inverted_image

def apply_gradient_map(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply the default gradient colormap
    gradient_map = cv2.applyColorMap(gray_image, cv2.COLORMAP_RAINBOW)

    # Blend the original image with the gradient map using transparency
    blended_image = cv2.addWeighted(image, 0.9, gradient_map, 0.1, 0)

    return blended_image

def apply_sunny_effect(image):
    # Adjusted sunny matrix for a lighter effect
    sunny_matrix = np.array([[1.1, 0.1, 0.0],
                             [0.1, 1.1, 0.0],
                             [0.0, 0.0, 1.0]])
    filtered_img = cv2.transform(image, sunny_matrix)
    
    # Adjusted brightness values for a lighter effect
    filtered_img = cv2.convertScaleAbs(filtered_img, alpha=1.1, beta=10)
    
    # Clip and normalize the values
    filtered_img = np.clip(filtered_img, 0, 255).astype(np.uint8)
    
    return filtered_img


def apply_tea_filter(image):
    tea_matrix = np.array([[1.0, 0.05, 0.0],
                           [0.1, 1.0, 0.1],
                           [0.0, 0.05, 1.0]])
    filtered_img = cv2.transform(image, tea_matrix)
    
    # Adjust intensity by clipping pixel values to a certain range
    intensity = 1  # Adjust this value to control the intensity
    filtered_img = np.clip(filtered_img * intensity, -1, 255).astype(np.uint8)
    
    return filtered_img


def apply_magenta_haze_effect(image):
    magenta_matrix = np.array([[0.8, 0.0, 0.6],
                                [0.1, 1.0, 0.1],
                                [0.4, 0.2, 0.8]])

    filtered_img = cv2.transform(image, magenta_matrix)
    return filtered_img

def apply_light_sepia_effect(image, intensity=0.5):
    sepia_matrix = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    
    sepia_effect = cv2.transform(image, sepia_matrix)
    light_sepia_effect = cv2.addWeighted(image, 1 - intensity, sepia_effect, intensity, 0)
    light_sepia_effect = np.clip(light_sepia_effect, 0, 255).astype(np.uint8)
    
    return light_sepia_effect

def apply_emboss_effect(image):
    kernel = np.array([[0, -1, -1],
                       [1, 0.9, -1],
                       [1, 1, 0]])
    embossed_image = cv2.filter2D(image, -1, kernel)
    return embossed_image

def apply_warm_effect(image):
    # Increase red channel and decrease blue channel
    blue, green, red = cv2.split(image)

    red = cv2.addWeighted(red, 1.2, 0, 0, 0)
    blue = cv2.addWeighted(blue, 0.7, 0, 0, 0)

    warm_effect_img = cv2.merge((blue, green, red))

    return warm_effect_img

def apply_vintage_effect(image):
    # Split the image into color channels
    blue, green, red = cv2.split(image)

    # Apply adjustments to each channel
    red = cv2.addWeighted(red, 1.2, 0, 0, 0)
    blue = cv2.addWeighted(blue, 0.9, 0, 0, 0)

    # Merge the channels back
    vintage_effect_img = cv2.merge((blue, green, red))

    return vintage_effect_img

def apply_sepia_effect(image):
    sepia_matrix = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia_effect_img = cv2.transform(image, sepia_matrix)

    return sepia_effect_img   

def apply_grayscale_effect(image):
    gray_effect_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_effect_img = cv2.cvtColor(gray_effect_img, cv2.COLOR_GRAY2BGR) 
    return gray_effect_img

def apply_sketch_effect(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    inverted_gray = cv2.bitwise_not(gray_image)

    # Apply Gaussian blur to the inverted image
    blurred_image = cv2.GaussianBlur(inverted_gray, (111, 111), 0)

    # Invert the blurred image
    inverted_blurred = cv2.bitwise_not(blurred_image)

    # Create the sketch effect by blending the original and inverted blurred images
    sketch = cv2.divide(gray_image, inverted_blurred, scale=256.0)

    return sketch

def apply_oil_painting_effect(image, radius=5):
    oil_painting_img = cv2.xphoto.createOilPainting(image, radius, 1)
    return oil_painting_img

def apply_posterization_effect(image, num_levels):
    # Apply posterization effect by reducing color levels
    quantized = np.floor_divide(image, 256 // num_levels)
    posterization_effect = np.uint8(quantized * (256 // num_levels))
    return posterization_effect

def apply_dreamy_effect(image):
    dreamy_matrix = np.array([[0.8, 0.2, 0.2],
                              [0.2, 0.8, 0.2],
                              [0.2, 0.2, 0.8]])
    dreamy_image = cv2.transform(image, dreamy_matrix)
    dreamy_image = np.clip(dreamy_image, 0, 255).astype(np.uint8)
    return dreamy_image

def apply_amaro_effect(image):
    # Apply a warm color filter
    amber_filter = np.array([[1.0, 0.0, 0.0],
                             [0.5, 1.0, 0.0],
                             [0.1, 0.2, 1.0]])
    image = cv2.transform(image, amber_filter)

    # Apply a faded look using alpha blending
    faded = cv2.addWeighted(image, 0.9, cv2.GaussianBlur(image, (0, 0), 30), 0.1, 0)

    return faded

def apply_beauty_filter(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise and smooth the image
    blurred = cv2.GaussianBlur(image, (0, 0), 10)

    # Divide the original image by the blurred image to create a high-pass filter effect
    high_pass = cv2.subtract(image, blurred)

    # Combine the high-pass filtered image with the original image to enhance details
    enhanced = cv2.addWeighted(image, 1.5, high_pass, -0.5, 0)

    return enhanced

def apply_valencia_filter(image):
    # Apply a brownish tint to the image
    brown_tint = np.array([[1.5, 0, 0], [0, 1.3, 0], [0, 0, 1]], dtype=np.float32)
    valencia_filtered = cv2.transform(image, brown_tint)

    # Increase the brightness of the image
    valencia_filtered = cv2.addWeighted(valencia_filtered, 1.2, valencia_filtered, 0, 10)

    return valencia_filtered


def apply_juno_filter(image):
    # Apply a bluish-green tint to the image
    bluish_green_tint = np.array([[1, 0, 0], [0, 1.1, 0], [0, 0, 1.2]], dtype=np.float32)
    juno_filtered = cv2.transform(image, bluish_green_tint)

    # Increase the contrast of the image
    juno_filtered = cv2.convertScaleAbs(juno_filtered, alpha=1.2, beta=0)

    return juno_filtered

def apply_xpro_ii_effect(image):
    # Increase the contrast
    increased_contrast = cv2.convertScaleAbs(image, alpha=1.5, beta=0)

    # Apply a color filter for a warm tone
    warm_tone_filter = np.array([[1.3, 0, 0], [0, 1.1, 0], [0, 0, 1]], dtype=np.float32)
    filtered_image = cv2.transform(increased_contrast, warm_tone_filter)

    return filtered_image

def apply_sharpening(image, amount=1):
    # Define the sharpening kernel
    kernel = np.array([[0, -1, 0],
                    [-1, 5, -1],
                    [0, -1, 0]])
    
    # Apply the kernel to the image
    sharpened = cv2.filter2D(image, -1, kernel)
    
    # Combine the original and sharpened images using the specified amount
    sharpened = cv2.addWeighted(image, 1 + amount, sharpened, -amount, 0)
    
    return sharpened

import cv2
import numpy as np

def apply_vsco_filter(image):
    # Convert image to float32 for processing
    img_float = image.astype(np.float32) / 255.0

    # Apply color adjustments
    adjusted_img = cv2.addWeighted(img_float, 1.1, img_float, 0, 0)  # Adjust brightness
    adjusted_img = cv2.addWeighted(adjusted_img, 1.1, img_float, 0, 10)  # Add a subtle warmth

    # Apply Reinhard tonemapping
    tonemap = cv2.createTonemapReinhard(gamma=0.8)
    tonemapped_img = tonemap.process(adjusted_img)

    # Add a subtle film-like grain
    h, w, _ = tonemapped_img.shape
    noise = np.random.normal(scale=0.04, size=(h, w, 3))
    filtered_img = np.clip(tonemapped_img + noise, 0, 10)

    # Convert back to uint8
    vsco_filtered_image = (filtered_img * 255).astype(np.uint8)

    return vsco_filtered_image

def apply_art_filter(image):
    # Convert image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Convert grayscale image to 8-bit
    gray_image_8bit = cv2.convertScaleAbs(gray_image)

    # Apply painterly effect using bilateral filter
    painterly = cv2.bilateralFilter(image, 9, 75, 75)

    # Enhance colors using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_color = clahe.apply(gray_image_8bit)

    # Load a texture overlay
    texture = cv2.imread('texture.jpg')
    texture = cv2.resize(texture, (image.shape[1], image.shape[0]))

    # Apply the texture overlay using blending
    blended = cv2.addWeighted(enhanced_color, 0.7, texture, 0.3, 0)

    # Combine the painterly effect and the blended image
    art_filter_result = cv2.addWeighted(painterly, 0.5, blended, 0.5, 0)

    return art_filter_result


def apply_sunned_up_effect(image):
    # Increase the brightness and contrast
    alpha = 1.2  # Contrast control (1.0 means no change)
    beta = 20    # Brightness control (0-100, 50 is a good starting point)

    sunned_up_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    # Apply a warm color tone
    yellow_color_matrix = np.array([[1, 0, 0],
                                    [0, 1.2, 0],
                                    [0, 0, 1.5]], dtype=np.float32)

    sunned_up_image = cv2.transform(sunned_up_image, yellow_color_matrix)

    return sunned_up_image
   
def apply_funky_effect(image):
    # Apply a color shift to create vibrant colors
    color_shift_matrix = np.array([[0.8, 0.2, 0],
                                   [0.1, 0.9, 0.1],
                                   [0, 0.2, 0.8]], dtype=np.float32)

    funky_image = cv2.transform(image, color_shift_matrix)

    # Increase the saturation
    hsv_image = cv2.cvtColor(funky_image, cv2.COLOR_BGR2HSV)
    hsv_image[:, :, 1] = hsv_image[:, :, 1] * 1.5  # Increase saturation by a factor
    funky_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    # Apply a barrel distortion
    height, width = funky_image.shape[:2]
    fx = 0.002  # Distortion factor along the horizontal axis
    fy = 0.002  # Distortion factor along the vertical axis
    distort_image = cv2.remap(funky_image, cv2.getOptimalNewCameraMatrix(None, None, (width, height), 1, (width, height), centerPrincipalPoint=False),
                              np.dstack(np.meshgrid(np.arange(width), np.arange(height)))[::-1].astype(np.float32) + np.array([np.cos(np.arange(height) * fy) * width * fx, np.arange(height)]).T, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    return distort_image   
   


def apply_saturation(img, saturation):
    # Adjust the saturation of the image
    himg = img.astype(np.float32) / 255.0
    
    # Apply saturation adjustment
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_img[:, :, 1] = np.clip(hsv_img[:, :, 1] + saturation * 255, 0, 255)
    img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

    return (img * 255).astype(np.uint8)

def apply_brightness(img, brightness):
    # Convert the image to float32 format for adjustment
    img = img.astype(np.float32) / 255.0
    
    # Calculate the scale factor for brightness adjustment based on the relationship
    if brightness > 0:
        scale_factor = (brightness-300) 
    else:
        scale_factor = 1 - (abs(brightness) * 0.7 / 100)

    # Apply brightness adjustment
    img = cv2.convertScaleAbs(img, alpha=scale_factor, beta=0)

    return (img * 255).astype(np.uint8)


# def apply_contrast(img, contrast):
#     # Adjust the contrast of the image
#     return cv2.convertScaleAbs(img, alpha=contrast / 100 + 1, beta=0)

# def apply_blur(img, blur):
  
#     return cv2.convertScaleAbs(img, alpha=70 / 100 + 1, beta=0)

# def apply_hue(img, hue):
#     # Adjust the hue of the image
#     hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#     hsv_img[:, :, 0] = np.clip(hsv_img[:, :, 0] + hue, 0, 179)
#     return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)        
  
  
