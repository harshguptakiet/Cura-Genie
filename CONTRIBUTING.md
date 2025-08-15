# 🤝 Contributing to CuraGenie

Thank you for considering contributing to **CuraGenie**! 🎉 Your support helps us improve and innovate in the field of AI-powered healthcare. Whether it's fixing bugs, adding features, or improving documentation, every contribution matters.

---

## 📜 Code of Conduct

By participating in this project, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md). We aim to maintain a friendly, safe, and respectful environment for everyone.

---

## 🚀 How to Contribute

### 1️⃣ Fork the Repository

* Click the **Fork** button at the top right of the repository page.
* This creates a copy of the project in your GitHub account.

### 2️⃣ Clone Your Fork

```bash
git clone https://github.com/your-username/CuraGenie.git
cd CuraGenie
```

### 3️⃣ Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use a descriptive name for your branch, like `feature/add-chatbot-tests` or `bugfix/fix-api-route`.

### 4️⃣ Make Your Changes ✏️

* Follow the **project structure** and maintain code quality.
* Add comments where necessary.
* Test your code before committing.

### 5️⃣ Commit Your Changes

```bash
git add .
git commit -m "✨ Added new feature: describe it here"
```

Use clear and descriptive commit messages. Prefix with emojis when possible (e.g., `🐛 fix`, `✨ feature`, `📝 docs`).

### 6️⃣ Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7️⃣ Create a Pull Request

* Go to the original repository on GitHub.
* Click **New Pull Request**.
* Provide a detailed description of your changes.
* Link any related issues.

---

## 🛠 Development Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Contribution Guidelines

* Follow consistent **coding style**.
* Keep **functions small and focused**.
* Write **clear documentation** for your code.
* Test your changes before submitting.
* If adding a new dependency, explain why it’s necessary.

---

## 🐞 Reporting Bugs

If you find a bug:

1. **Search** existing issues to avoid duplicates.
2. **Open a new issue** with a descriptive title.
3. Include:

   * Steps to reproduce
   * Expected behavior
   * Actual behavior
   * Screenshots (if applicable)

---

## 💡 Suggesting Features

We love new ideas! 💡

1. Check if the feature is already requested.
2. Open a new issue with:

   * **Problem statement**
   * **Proposed solution**
   * **Alternatives considered**

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Built with ❤️ by the **CuraGenie** community to advance personalized healthcare through AI and genomics.
