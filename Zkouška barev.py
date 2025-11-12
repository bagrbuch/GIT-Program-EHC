import matplotlib.pyplot as plt
import numpy as np

# vytvoříme gradient
gradient = np.linspace(0, 1, 256).reshape(1, -1)

# seznam colormap
cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']

fig, axes = plt.subplots(len(cmaps), 2, figsize=(6, 6))
for i, cmap_name in enumerate(cmaps):
    cmap = plt.get_cmap(cmap_name)
    axes[i, 0].imshow(gradient, aspect='auto', cmap=cmap)
    axes[i, 0].set_title(cmap_name)
    axes[i, 0].axis('off')

    # převedeno do šedé (pomocí luminance)
    gray = np.dot(cmap(np.linspace(0, 1, 256))[:, :3], [0.299, 0.587, 0.114])
    axes[i, 1].imshow(gray.reshape(1, -1), aspect='auto', cmap='gray')
    axes[i, 1].axis('off')

plt.tight_layout()
plt.show()
