# forms.py
import base64
from django import forms
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from .models import ProductImage

class CameraCaptureWidget(forms.ClearableFileInput):
    """
    A custom widget that adds webcam capture functionality using getUserMedia.
    It uses adapter.js for cross-browser support and falls back to file upload
    if getUserMedia is not available.
    """
    def render(self, name, value, attrs=None, renderer=None):
        # Render the standard file input widget
        input_html = super().render(name, value, attrs, renderer)
        
        # Extra HTML & JavaScript for webcam capture
        extra_html = f"""
            <!-- Include adapter.js from a CDN -->
            <script src="https://webrtc.github.io/adapter/adapter-latest.js"></script>
            <div class="camera-capture">
              <button type="button" id="openCameraBtn_{name}" onclick="window.openCamera_{name}()">Capture from Webcam</button>
              <div id="cameraContainer_{name}" style="display:none; margin-top:10px;">
                  <video id="video_{name}" width="320" height="240" autoplay style="border:1px solid #ccc;"></video>
                  <br>
                  <button type="button" onclick="window.captureImage_{name}()">Capture</button>
                  <canvas id="canvas_{name}" width="320" height="240" style="display:none;"></canvas>
                  <br>
                  <img id="preview_{name}" src="" alt="Captured image preview" style="display:none; border:1px solid #ccc;"/>
              </div>
              <input type="hidden" name="captured_{name}" id="captured_{name}">
              <div id="fallbackMsg_{name}" style="color: red; margin-top: 10px;"></div>
            </div>
            <script>
              // Check for getUserMedia support
              if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
                  document.getElementById("openCameraBtn_{name}").style.display = "none";
                  document.getElementById("fallbackMsg_{name}").innerHTML = "Webcam capture is not supported in this browser. Please use file upload instead.";
              }}

              // Attach functions to the global window object
              window.openCamera_{name} = function() {{
                  var container = document.getElementById("cameraContainer_{name}");
                  container.style.display = "block";
                  var video = document.getElementById("video_{name}");
                  navigator.mediaDevices.getUserMedia({{ video: true }})
                      .then(function(stream) {{
                          video.srcObject = stream;
                          video.play();
                      }})
                      .catch(function(err) {{
                          console.error("Error accessing webcam: " + err);
                          document.getElementById("fallbackMsg_{name}").innerHTML = "Error accessing webcam. Please use file upload instead.";
                      }});
              }};
              window.captureImage_{name} = function() {{
                  var video = document.getElementById("video_{name}");
                  var canvas = document.getElementById("canvas_{name}");
                  var context = canvas.getContext("2d");
                  context.drawImage(video, 0, 0, canvas.width, canvas.height);
                  var dataURL = canvas.toDataURL("image/png");
                  document.getElementById("preview_{name}").src = dataURL;
                  document.getElementById("preview_{name}").style.display = "block";
                  document.getElementById("captured_{name}").value = dataURL;
              }};
            </script>
        """
        return mark_safe(input_html + extra_html)
class ProductImageForm(forms.ModelForm):
    captured_image = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = ProductImage
        fields = ('image', 'is_primary', 'captured_image')
        widgets = {
            'image': CameraCaptureWidget(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        captured_data = cleaned_data.get('captured_image')
        image = cleaned_data.get('image')
        if captured_data and not image:
            try:
                format, imgstr = captured_data.split(';base64,')
            except ValueError:
                raise forms.ValidationError("Invalid captured image data.")
            ext = format.split('/')[-1]
            decoded_file = base64.b64decode(imgstr)
            file_name = f"captured_image.{ext}"
            cleaned_data['image'] = ContentFile(decoded_file, name=file_name)
        return cleaned_data




# forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Name")
    email = forms.EmailField(label="Email")
    subject = forms.CharField(max_length=200, label="Subject")
    message = forms.CharField(widget=forms.Textarea, label="Message")
