# HERBS
A Python-based GUI for Histological E-data Registration in Brain Space


HERBS is an open source, extensible, intuitive and interactive software platform for image visualisation and image registration. Where the image registration is the process of identifying a spatial transformation that maps images to a template such that corresponding anatomical structures are optimally aligned, or in other words, a voxel-wise ‘correspondence’ is established between the images and template.

HERBS has been tested on Windows (10 and 11), MacOSx (Mojave - Monterey), Linux (Kubuntu 18.04), and as a python application, it should run in all environments supporting python 3.8-3.10 and PyQt5 5.15.4 as a GUI framework. For details, please see HERBS CookBook (coming soon).

HERBS provides users:

- 2D and 3D visualisation of brain atlas volume data and arbitrary slicing.
- Image registration with interactive local elastic deformation methods in current version.
- 2D and 3D visualisation of user defined data.

## Install

```python
$ pip install herbs
```

## Usage

```python
import herbs
herbs.run_herbs()
```

After running the above scripts, a GUI window will pop up. Users can download atlas and upload images for further process,

<img src="herbs/herbs.png" width="800px"></img>

For more information, please read HERBS CookBook (coming soon) or check the Tutorial folder for corresponding functionalities.

### 
Please report your issues: https://github.com/JingyiGF/HERBS/issues. Please have a good description (maybe a screenshot or an error message). Any feedback welcome!

Please feel free to start any discussion: https://github.com/JingyiGF/HERBS/discussions.

## Finally
HERBS is 'always' in development, please check updates every time before you use it.


Hope this tool makes your amazing research life more tasty,
Mvh, Jingyi GF
