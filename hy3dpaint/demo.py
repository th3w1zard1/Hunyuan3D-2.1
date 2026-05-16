# Hunyuan 3D is licensed under the TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT
# except for the third-party components listed below.
# Hunyuan 3D does not impose any additional limitations beyond what is outlined
# in the repsective licenses of these third-party components.
# Users must comply with all terms and conditions of original licenses of these third-party
# components and must ensure that the usage of the third party components adheres to
# all relevant laws and regulations.

# For avoidance of doubts, Hunyuan 3D means the large language models and
# their software and algorithms, including trained model weights, parameters (including
# optimizer states), machine-learning model code, inference-enabling code, training-enabling code,
# fine-tuning enabling code and other elements of the foregoing made publicly available
# by Tencent in accordance with TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT.

try:
    from hy3dpaint.runtime_compat import exit_if_unsupported_runtime_python
    from hy3dpaint.bootstrap import apply_torchvision_compatibility_fix
    from hy3dpaint.glb_support import is_glb_conversion_available
    from hy3dpaint.textureGenPipeline import (
        Hunyuan3DPaintConfig,
        Hunyuan3DPaintPipeline,
    )
except ImportError:
    from runtime_compat import exit_if_unsupported_runtime_python
    from bootstrap import apply_torchvision_compatibility_fix
    from glb_support import is_glb_conversion_available
    from textureGenPipeline import Hunyuan3DPaintConfig, Hunyuan3DPaintPipeline

exit_if_unsupported_runtime_python()
apply_torchvision_compatibility_fix()


if __name__ == "__main__":
    max_num_view = 6  # can be 6 to 9
    resolution = 512  # can be 768 or 512

    conf = Hunyuan3DPaintConfig(max_num_view, resolution)
    paint_pipeline = Hunyuan3DPaintPipeline(conf)
    save_glb = is_glb_conversion_available()
    if not save_glb:
        print("bpy is not available; saving the textured mesh as OBJ instead of GLB.")
    output_mesh_path = paint_pipeline(
        mesh_path="./assets/case_1/mesh.glb",
        image_path="./assets/case_1/image.png",
        output_mesh_path=(
            "./assets/case_1/textured_mesh.glb"
            if save_glb
            else "./assets/case_1/textured_mesh.obj"
        ),
        save_glb=save_glb,
    )
    print(f"Output mesh path: {output_mesh_path}")
