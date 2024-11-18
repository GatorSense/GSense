---
icon: monitor-waveform
---

# Spectral Indexing

Spectral indexing empowers users to apply mathematical functions to spectral indices/bands, which can reveal specific characteristics or anomalies within images. This tool is valuable in areas such as remote sensing and agricultural analysis, where understanding spectral differences can lead to significant insights.

<figure><img src="../.gitbook/assets/image (3) (1).png" alt="" width="363"><figcaption></figcaption></figure>

**Using Spectral Indexing**:

1. Enter channel expressions for the Red, Green, and Blue channels in the text boxes (e.g., `ch[50]`, `ch[100]*2`, `ch[25]/ch[10]`).
2. Press `Enter` or click "Compute" to generate the images.
3. Images with invalid indices will be skipped, and a warning will be displayed.

**Multiple Pseudo-RGBs**:

Users can compute multiple pseudo-RGB images per batch. Each set is saved and accessible via the interface.

