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

from .pipelines import Hunyuan3DDiTPipeline as Hunyuan3DDiTPipeline
from .pipelines import (
	Hunyuan3DDiTFlowMatchingPipeline as Hunyuan3DDiTFlowMatchingPipeline,
)
from .preprocessors import DEFAULT_IMAGEPROCESSOR as DEFAULT_IMAGEPROCESSOR
from .preprocessors import IMAGE_PROCESSORS as IMAGE_PROCESSORS
from .preprocessors import ImageProcessorV2 as ImageProcessorV2


def _missing_optional_postprocessor(name, error):
	class MissingOptionalPostprocessor:
		def __init__(self, *args, **kwargs):
			raise ModuleNotFoundError(
				f"pymeshlab is required to use {name}. Install the full mesh post-processing runtime."
			) from error

	MissingOptionalPostprocessor.__name__ = name
	return MissingOptionalPostprocessor


try:
	from .postprocessors import (  # type: ignore[assignment]
		FaceReducer as FaceReducer,
		FloaterRemover as FloaterRemover,
		DegenerateFaceRemover as DegenerateFaceRemover,
		MeshSimplifier as MeshSimplifier,
	)
except ModuleNotFoundError as error:
	if getattr(error, "name", None) != "pymeshlab":
		raise

	FaceReducer = _missing_optional_postprocessor("FaceReducer", error)
	FloaterRemover = _missing_optional_postprocessor("FloaterRemover", error)
	DegenerateFaceRemover = _missing_optional_postprocessor(
		"DegenerateFaceRemover", error
	)
	MeshSimplifier = _missing_optional_postprocessor("MeshSimplifier", error)
