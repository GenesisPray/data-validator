# 🚀 How to Host This Web App on GitHub Pages (Step-by-Step)

This application is **100% static and client-side**. It has zero server requirements, which means you can host it on **GitHub Pages** for **free 24/7**.

Once hosted, you and your colleagues will get a permanent public link:
`https://<your-github-username>.github.io/<your-repo-name>/`

---

## Method 1: Upload via GitHub Web Browser (No Git Required — 2 Minutes)

If you don't have Git installed on your computer, you can do this directly from your web browser:

1. **Log into GitHub**:
   - Go to [https://github.com](https://github.com) and log in.

2. **Create a New Repository**:
   - Click the **`+`** icon in the top right corner and select **New repository**.
   - **Repository name**: e.g., `data-validator` or `medbalance`
   - **Visibility**: Choose **Public** (required for free GitHub Pages).
   - Leave "Initialize with README" **unchecked** (we already have one).
   - Click **Create repository**.

3. **Upload Your Files**:
   - On the next screen, click the link that says **"uploading an existing file"**.
   - Drag and drop all the files from your folder `c:\Users\DELL PC\Desktop\Data Validator` into the browser:
     - `index.html` *(essential)*
     - `.nojekyll`
     - `README.md`
     - `sample_inventory_data.csv`
     - `template_inventory.csv`
     - `flagged.csv`
     - `.github/` folder (if uploading via web, you can create it later or use the simple Settings option below)
   - At the bottom, click the green **Commit changes** button.

4. **Turn On GitHub Pages**:
   - In your repository, click **Settings** (tab at the top right).
   - On the left sidebar menu, click **Pages** (under "Code and automation").
   - Under **Build and deployment**:
     - **Source**: Select `Deploy from a branch`.
     - **Branch**: Select `main` (or `master`), folder: `/ (root)`.
     - Click **Save**.

5. **Access Your Live Website**:
   - Wait about 30 to 60 seconds.
   - Refresh the **Pages** settings screen. You will see a banner:
     > **"Your site is live at https://<username>.github.io/<repo-name>/"**
   - Click that link to open and share your live web app!

---

## Method 2: Push via GitHub Desktop or Git

If you use **GitHub Desktop**:
1. Open GitHub Desktop and click **File** -> **Add Local Repository...**
2. Choose `c:\Users\DELL PC\Desktop\Data Validator`.
3. Click **Publish repository** to GitHub.
4. Go to **Settings** -> **Pages** on your repository on GitHub and select `Deploy from a branch` -> `main` / `root`.

---

## Why GitHub Pages Works Perfectly for This App:
- **No Python or server required**: All stock calculations ($BB + REC - DISP - LOSS = EB$), column recognition, and file filtering execute entirely in the user's browser.
- **Data privacy & security**: Facilities can upload their CSVs safely because the data never leaves their local browser.
- **Fast & Responsive**: Instant audits on desktop, tablets, and smartphones.
- **Exports work everywhere**: "Download flagged.csv" and "Blank Template" generate standard CSV files directly in the browser.
