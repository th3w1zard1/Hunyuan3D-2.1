from PIL import Image
from hy3dpaint.runtime_compat import exit_if_unsupported_runtime_python
from hy3dpaint.bootstrap import apply_torchvision_compatibility_fix
from hy3dpaint import Hunyuan3DPaintConfig, Hunyuan3DPaintPipeline
from hy3dpaint.glb_support import is_glb_conversion_available
from hy3dshape.rembg import BackgroundRemover
from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline

exit_if_unsupported_runtime_python()
apply_torchvision_compatibility_fix()

# shape
model_path = "tencent/Hunyuan3D-2.1"
pipeline_shapegen = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(model_path)

image_path = "assets/demo.png"
image = Image.open(image_path).convert("RGBA")
if image.mode == "RGB":
    rembg = BackgroundRemover()
    image = rembg(image)

mesh = pipeline_shapegen(image=image)[0]
mesh.export("demo.glb")

# paint
max_num_view = 6  # can be 6 to 9
resolution = 512  # can be 768 or 512
conf = Hunyuan3DPaintConfig(max_num_view, resolution)
paint_pipeline = Hunyuan3DPaintPipeline(conf)

save_glb = is_glb_conversion_available()
output_mesh_path = "demo_textured.glb" if save_glb else "demo_textured.obj"
if not save_glb:
    print("bpy is not available; saving the textured mesh as OBJ instead of GLB.")
output_mesh_path = paint_pipeline(
    mesh_path="demo.glb",
    image_path="assets/demo.png",
    output_mesh_path=output_mesh_path,
    save_glb=save_glb,
)
print(f"Output mesh path: {output_mesh_path}")
