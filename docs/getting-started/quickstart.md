---
icon: sign-posts-wrench
---

# Installation

#### Clone the repository:

```bash
git clone https://github.com/GatorSense/GSense.git
```

#### Set up an environment (recommended):

{% tabs %}
{% tab title="Using venv (Python >= 3.9)" %}
```
python3 -m venv gsense_env
source gsense_env/bin/activate   # On Linux/macOS
gsense_env\Scripts\activate      # On Windows
```
{% endtab %}

{% tab title="Using conda" %}
```
conda create -n gsense_env python=3.9
conda activate gsense_env
```
{% endtab %}
{% endtabs %}

#### Navigate into the GSense directory and install the dependencies:

```bash
cd GSense
pip install .
```

#### Install `torch` based on your system's GPU capability:

{% tabs %}
{% tab title="For systems without a GPU" %}
```
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

###

#### Running the Application

After installation, you can run the application using the following command:

{% hint style="info" %}
Want to learn about writing content from scratch? Head to the [Basics](https://github.com/GitbookIO/onboarding-template/blob/main/getting-started/broken-reference/README.md) section to learn more.
{% endhint %}

### Running GSense

```
gsense
```

or

```
python -m app.main
```



### Interface

<figure><img src="../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>



### Import

GitBook supports importing content from many popular writing tools and formats. If your content already exists, you can upload a file or group of files to be imported.

<div data-full-width="false">

<figure><img src="https://gitbookio.github.io/onboarding-template-images/quickstart-import.png" alt=""><figcaption></figcaption></figure>

</div>

### Sync a repository

GitBook also allows you to set up a bi-directional sync with an existing repository on GitHub or GitLab. Setting up Git Sync allows you and your team to write content in GitBook or in code, and never have to worry about your content becoming out of sync.
