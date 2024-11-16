---
icon: sign-posts-wrench
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Installation

### Clone the repository:

```bash
git clone https://github.com/GatorSense/GSense.git
```

***

### Set up an environment (recommended):

{% tabs %}
{% tab title="Using venv (Python >= 3.9)" %}
```bash
python3 -m venv gsense_env
source gsense_env/bin/activate   # On Linux/macOS
gsense_env\Scripts\activate      # On Windows
```
{% endtab %}

{% tab title="Using conda" %}
```bash
conda create -n gsense_env python=3.9
conda activate gsense_env
```
{% endtab %}
{% endtabs %}

***

### Navigate into the GSense directory and install the dependencies:

***

```bash
cd GSense
pip install .
```

#### Install `torch` based on your system's GPU capability:

{% tabs %}
{% tab title="For systems without a GPU" %}
```bash
pip install torch torchvision torchaudio
```
{% endtab %}

{% tab title="For systems with a CUDA-enabled GPU" %}
Please refer to the [PyTorch website](https://pytorch.org/get-started/locally/) for specific PyTorch and Torchvision installation instructions based on your system.
{% endtab %}
{% endtabs %}

{% hint style="info" %}
Installing PyTorch and torchvision with CUDA support is strongly recommended.
{% endhint %}

### Running the Application

After installation, you can run the application using the following command:

```
gsense
```

or

```
python -m app.main
```

### Interface

<figure><img src="../.gitbook/assets/image (16).png" alt=""><figcaption></figcaption></figure>
