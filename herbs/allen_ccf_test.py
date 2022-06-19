import numpy as np
import nrrd
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os
import requests
import pyqtgraph.opengl as gl
from Archived.HERBS.herbs.uuuuuu import hex2rgb

atlas_file = '/Users/jingyig/Work/Kavli/AllenCCF10um/average_template_10.nrrd'
volume_data, header = nrrd.read(atlas_file)
print(volume_data.shape)
print(header)

volume_data = np.transpose(volume_data[::-1, ::-1, :], (2, 0, 1))
outfile_at = open('Allen_CCF_v3_10um_template.pkl', 'wb')
pickle.dump(volume_data, outfile_at)
outfile_at.close()


filename = '/Users/jingyig/Work/Kavli/AllenCCF10um/annotation_10.nrrd'

label_data, header = nrrd.read(filename)
print(label_data.shape)
print(header)

label_data = np.transpose(label_data[::-1, ::-1, :], (2, 0, 1))

outfile_seg = open('Allen_CCF_v3_10um_annotation.pkl', 'wb')
pickle.dump(label_data, outfile_seg)
outfile_seg.close()


valid_annotation = np.unique(label_data)
len(valid_annotation)  # 673 contains 0
print(valid_annotation)
np.min(valid_annotation)  # 0
np.max(valid_annotation)  # 614454277

csv_file_path = '/Users/jingyig/Work/Kavli/AllenCCF10um/query.csv'

df = pd.read_csv(csv_file_path)
dfs_keys = list(df.keys())


da_labels = df['safe_name'].values
for i in range(len(da_labels)):
    if da_labels[i] == 'root':
        da_labels[i] = 'Brain'

da_short_label = df['acronym'].values
for i in range(len(da_short_label)):
    if da_short_label[i] == 'root':
        da_short_label[i] = 'Brain'

hex_colors = df['color_hex_triplet'].values
rgb_colors = []
for i in range(len(hex_colors)):
    r, g, b = hex2rgb(hex_colors[i])
    rgb_colors.append([r, g, b])
rgb_colors = np.asarray(rgb_colors)

levels = []
structure_id_path = df['structure_id_path'].values
for i in range(len(structure_id_path)):
    da_path = structure_id_path[i]
    da_path_split = da_path.split('/')
    for j in np.arange(len(da_path_split))[::-1]:
        if da_path_split[j] == '':
            da_path_split.pop(j)
    levels.append(len(da_path_split))

label_info = {'index': df['id'].values.astype(int),
              'label': da_labels,
              'parent': df['parent_structure_id'].values.astype(int),
              'abbrev': da_short_label,
              'color': rgb_colors,
              'level_indicator': levels}

with open('atlas_labels.pkl', 'wb') as handle:
    pickle.dump(label_info, handle, protocol=pickle.HIGHEST_PROTOCOL)




for ind in valid_annotation:
    if ind == 0:
        continue
    url = 'http://download.alleninstitute.org/informatics-archive/current-release/mouse_ccf/annotation/ccf_2017/structure_meshes/{}.obj'.format(ind)
    r = requests.get(url, allow_redirects=True)
    da_file = open('/Users/jingyig/Work/Kavli/AllenCCF10um/meshes/{}.obj'.format(ind), 'wb')
    da_file.write(r.content)
    da_file.close()


def obj_data_to_mesh3d(filename):
    vertices = []
    faces = []

    with open(filename, 'r') as objf:
        for line in objf:
            slist = line.split()
            if slist:
                if slist[0] == 'v':
                    vertex = np.array(slist[1:], dtype=float)
                    vertices.append(vertex)
                elif slist[0] == 'f':
                    face = []
                    for k in range(1, len(slist)):
                        face.append([int(s) for s in slist[k].replace('//', '/').split('/')])
                    if len(face) > 3:  # triangulate the n-polyonal face, n>3
                        faces.extend(
                            [[face[0][0] - 1, face[k][0] - 1, face[k + 1][0] - 1] for k in range(1, len(face) - 1)])
                    else:
                        faces.append([face[j][0] - 1 for j in range(len(face))])
                else:
                    pass

    return np.array(vertices), np.array(faces)

for ind in valid_annotation:
    print(ind)
    if ind in [545, 0]:
        continue

    filename = '/Users/jingyig/Work/Kavli/AllenCCF10um/downloaded_meshes/{}.obj'.format(ind)

    vertices, faces = obj_data_to_mesh3d(filename)
    vertices = vertices / 10

    vertices[:, 0] = 1320 - vertices[:, 0]
    vertices[:, 1] = 800 - vertices[:, 1]

    verts = vertices.copy()
    verts[:, 0] = vertices[:, 2].copy()
    verts[:, 1] = vertices[:, 0].copy()
    verts[:, 2] = vertices[:, 1].copy()


    md = gl.MeshData(vertexes=verts, faces=faces)

    outfile = open(os.path.join('/Users/jingyig/Work/Kavli/AllenCCF10um/meshes/', '{}.pkl'.format(ind)), 'wb')
    pickle.dump(md, outfile)
    outfile.close()

d = np.unique(ddd[ddd > 0])
len(d)  # 591 ?????



plt.imshow(data[600, :, :])
plt.show()

plt.imshow(data[300, :, :])
plt.show()

plt.imshow(data[1200, :, :])
plt.show()

# cut x axis is coronal cut, 0 is front

plt.imshow(data[:, 30, :])
plt.show()

plt.imshow(data[:, 400, :])
plt.show()

plt.imshow(data[:, 750, :])
plt.show()

# cut y is horizontal cut, 0 is top

plt.imshow(data[:, 30, :])
plt.show()

plt.imshow(data[:, 400, :])
plt.show()

plt.imshow(data[:, 750, :])
plt.show()