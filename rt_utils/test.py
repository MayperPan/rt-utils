import os
import numpy as np
import nibabel as nib
import pydicom
import matplotlib.pyplot as plt
from glob import glob
import warnings

warnings.filterwarnings("ignore")


def load_dicom_series(directory: str) -> np.ndarray:
    """
    读取指定文件夹中的DICOM序列，并按SliceLocation或InstanceNumber排序，返回3D体积。
    如文件夹无有效DICOM文件或文件缺失，返回空数组(None)。
    """
    # 获取文件夹内所有.dcm文件
    dicom_files = glob(os.path.join(directory, "*.dcm"))
    if not dicom_files:
        # 如果没有.dcm后缀，尝试读取所有文件
        all_files = glob(os.path.join(directory, "*"))
        dicom_files = [f for f in all_files if os.path.isfile(f)]

    # 尝试读取每个文件，收集有效的DICOM数据集
    datasets = []
    for f in dicom_files:
        try:
            ds = pydicom.dcmread(f, force=True)
            # 确保有像素数据
            if hasattr(ds, 'pixel_array'):
                datasets.append(ds)
        except Exception:
            continue

    if not datasets:
        print(f"警告: 在 {directory} 中没有找到有效的DICOM文件。")
        return None

    # 根据SliceLocation排序，若缺失则使用InstanceNumber
    if hasattr(datasets[0], 'SliceLocation'):
        datasets.sort(key=lambda x: float(x.SliceLocation))
    else:
        datasets.sort(key=lambda x: int(x.InstanceNumber))

    # 构建3D数组
    slices = []
    for ds in datasets:
        pixel_array = ds.pixel_array.astype(np.float32)
        # 应用RescaleSlope/RescaleIntercept（如果存在）
        if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
            pixel_array = ds.RescaleSlope * pixel_array + ds.RescaleIntercept
        slices.append(pixel_array)

    volume = np.stack(slices, axis=-1)
    print(f"成功加载DICOM序列，形状: {volume.shape}")
    return volume


def show_nifti_and_dicom(nifti_path: str, dicom_dir: str):
    """
    加载并显示NIfTI文件和对应的DICOM序列。
    """
    # 1. 加载NIfTI
    nifti_img = nib.load(nifti_path)
    # 使用 get_fdata() 读取数据矩阵
    label_data = nifti_img.get_fdata()

    nifti_data = np.transpose(label_data, (1, 0, 2))


    # 2. 加载DICOM序列
    dicom_volume = load_dicom_series(dicom_dir)
    if dicom_volume is None:
        print("DICOM加载失败，将只显示NIfTI。")
        # 只显示NIfTI
        plt.figure(figsize=(12, 6))
        mid_slice = nifti_data.shape[2] // 2
        plt.imshow(nifti_data[:, :, mid_slice], cmap='gray')
        plt.title("NIfTI (Middle Slice)")
        plt.axis('off')
        plt.show()
        return

    # 3. 显示对比
    # 选择一个中间切片索引（假定Z轴是最后一个维度）
    # z_index = min(nifti_data.shape[2], dicom_volume.shape[2]) // 3
    z_index = 7


    # 提取对应的2D切片
    nifti_slice = nifti_data[:, :, z_index]  # 假设形状为 (X, Y, Z)
    dicom_slice = dicom_volume[:, :, z_index]  # 假设形状为 (X, Y, Z)

    # 归一化以便显示（可选）
    nifti_slice = (nifti_slice - nifti_slice.min()) / (nifti_slice.max() - nifti_slice.min() + 1e-8)
    dicom_slice = (dicom_slice - dicom_slice.min()) / (dicom_slice.max() - dicom_slice.min() + 1e-8)

    # 并排显示
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(nifti_slice, cmap='gray')
    axes[0].set_title(f"NIfTI (切片 {z_index})")
    axes[0].axis('off')

    axes[1].imshow(dicom_slice, cmap='gray')
    axes[1].set_title(f"DICOM (切片 {z_index})")
    axes[1].axis('off')

    plt.tight_layout()
    plt.show()


# ====== 使用示例 ======
if __name__ == "__main__":
    # 请替换为您的实际文件路径
    nifti_file = r'C:\Users\Administrator\Desktop\RT01189\nii\Untitled.nii.gz'  # NIfTI文件路径
    dicom_folder = r"C:\Users\Administrator\Desktop\RT01189\T1c"  # DICOM序列文件夹路径

    show_nifti_and_dicom(nifti_file, dicom_folder)