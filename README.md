# 🔐 PII Audio Redaction Pipeline

Automatically **detect and remove sensitive personal information (PII) from Hindi audio files** using Azure AI and audio processing.

## 🤔 What is PII Removal?

**PII (Personally Identifiable Information)** includes sensitive data like:
- 👤 **Names** - "मेरा नाम राहुल है"
- 📱 **Phone Numbers** - "मेरा नंबर 9876543210 है" 
- 🆔 **ID Numbers** - Aadhaar, PAN, etc.
- 📧 **Email Addresses**
- 🏠 **Addresses**

**PII Removal** means finding these sensitive parts in audio and **muting/silencing** them to protect privacy while keeping the rest of the conversation intact.

## ✨ What This Tool Does

1. 🎙️ **Converts** Hindi speech to text with timestamps
2. 🕵️ **Finds** PII in the transcript  
3. ⏱️ **Maps** PII back to exact audio locations
4. 🔇 **Mutes** those audio segments
5. 💾 **Saves** clean audio file

**Example**: 
- **Input**: "Hello, मेरा नाम अनिल है और मेरा फोन 9876543210 है"
- **Output**: "Hello, [MUTED] है और मेरा फोन [MUTED] है"

## 🚀 How to Use

### 1. Clone the Repository

```bash
git clone https://github.com/AnirudhPradhan/pii-audio-redaction.git
cd pii-audio-redaction
```

### 2. Install Dependencies

Make sure you have Python 3.8+ installed. Then run:

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

Create a `.env` file in the project root with your Azure keys:

```env
SPEECH_KEY=your_speech_key_here
SPEECH_ENDPOINT=https://your-region.stt.speech.microsoft.com/
LANGUAGE_KEY=your_language_key_here  
LANGUAGE_ENDPOINT=https://your-region.cognitiveservices.azure.com/
```

### 4. Run the Pipeline

Place your Hindi audio file (e.g., `input.wav`) in the inputs directory and run pipeline.ipynb step by step

The redacted audio will be saved at output_audio.

## 🔑 Required Credentials

| Service | What You Need | Where to Get |
|---------|---------------|--------------|
| **Azure Speech Services** | Speech Key + Endpoint | [Azure Portal](https://portal.azure.com) → Speech Services |
| **Azure Text Analytics** | Language Key + Endpoint | [Azure Portal](https://portal.azure.com) → Language Services |

## 🎯 Use Cases

- **Call Centers** - Remove customer PII from recordings
- **Interviews** - Protect candidate privacy  
- **Medical Records** - Anonymize patient conversations
- **Legal Audio** - Redact sensitive client information
- **Research** - Clean datasets for analysis

## 🙌 Acknowledgements

- Thanks to the open-source community for tools and inspiration.
- Special appreciation to Microsoft Azure for providing powerful APIs for language and speech understanding.

---

## 🤝 Contributing

We welcome contributions to make this project better! To get started:

1. **Fork** the repository on GitHub.
2. **Create a new branch** for your feature or fix:
    ```bash
    git checkout -b your-feature-name
    ```
3. **Make your changes** and add clear, descriptive commit messages:
    ```bash
    git commit -m "Describe your changes"
    ```
4. **Push your branch** to your fork:
    ```bash
    git push origin your-feature-name
    ```
5. **Open a pull request** on GitHub and describe your changes.

---
## 📞 Support

**Made by**: Anirudh Pradhan (IIIT Bhubaneswar)  
**Email**: anirudh@example.com  
**Issues**: Create GitHub issue for bugs

## 📜 License
This project is licensed under the **MIT License**.

---

## 📬 Contact
For any questions or suggestions, feel free to reach out:

👤 **Author:** Anirudh Pradhan  
🔗 **GitHub:** [AnirudhPradhan](https://github.com/AnirudhPradhan)

---
*"Protecting privacy, one audio file at a time" 🔇*
