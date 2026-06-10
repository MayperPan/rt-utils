from rt_utils import RTStructBuilder

# Create new RT Struct. Requires the DICOM series path for the RT Struct.
rtstruct = RTStructBuilder.create_new(dicom_series_path=r"C:\Users\Administrator\Desktop\RT01189\T1c")

# ...
# Create mask through means such as ML
# ...

import nibabel as nib
import numpy as np

# 加载 NIfTI 文件
nifti_file = nib.load(r'C:\Users\Administrator\Desktop\RT01189\nii\Untitled.nii.gz')

print(f'原始形状：{nifti_file.shape}')

# 获取图像数据为 NumPy 数组

MASK_FROM_ML_MODEL = nifti_file.get_fdata()

# 交换第 0 维和第 1 维（x 和 y 互换）        [读取ITK勾画保存的nii后必须转换XY对称，否则生成的rt结构是中心对称的]
MASK_FROM_ML_MODEL = np.transpose(MASK_FROM_ML_MODEL, (1, 0, 2))

print(f'转换后形状：{MASK_FROM_ML_MODEL.shape}')

#转换为boolean型
MASK_FROM_ML_MODEL =MASK_FROM_ML_MODEL.astype(bool)


print(type(MASK_FROM_ML_MODEL))  # <class 'numpy.ndarray'>
print(MASK_FROM_ML_MODEL)  # 输出数组的维度，例如 (128, 128, 90)


# Add the 3D mask as an ROI.
# The colour, description, and name will be auto generated



rtstruct.add_roi(mask=MASK_FROM_ML_MODEL)

# Add another ROI, this time setting the color, description, and name
rtstruct.add_roi(
  mask=MASK_FROM_ML_MODEL,
  color=[255, 0, 255],
  name="RT-Utils ROI!"
)

rtstruct.save(r'C:\Users\Administrator\Desktop\RT01189\T1c\new-rt-struct')

from rt_utils import RTStructBuilder
import matplotlib.pyplot as plt

# # Load existing RT Struct. Requires the series path and existing RT Struct path
# rtstruct = RTStructBuilder.create_from(
#   dicom_series_path="./testlocation",
#   rt_struct_path="./testlocation/rt-struct.dcm"
# )
#
# # View all of the ROI names from within the image
# print(rtstruct.get_roi_names())
#
# # Loading the 3D Mask from within the RT Struct
# mask_3d = rtstruct.get_roi_mask_by_name("ROI NAME")
#
# # Display one slice of the region
# first_mask_slice = mask_3d[:, :, 0]
# plt.imshow(first_mask_slice)
# plt.show()