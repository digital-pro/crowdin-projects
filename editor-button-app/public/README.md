# 🎵 Levante Audio Test - User Guide

A Crowdin app for generating and playing audio for translations using PlayHT and ElevenLabs text-to-speech services.

## 📋 Table of Contents

- [Installation](#installation)
- [Setup & Configuration](#setup--configuration)
- [How to Use](#how-to-use)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## 🚀 Installation

### Step 1: Install the Crowdin App

1. **Go to your Crowdin project**
2. **Navigate to**: Settings → Integrations → Applications
3. **Click**: "Install Custom App" or "Add Application"
4. **Enter the manifest URL**: 
   ```
   https://levante-audio-test.vercel.app/manifest.json
   ```
5. **Click**: Install/Add

### Step 2: Access the App

1. **Open the Crowdin Editor** for your project
2. **Look for** "🎤 Levante Audio Test" in the right panel
3. **Click** to open the app

## ⚙️ Setup & Configuration

### Configure API Credentials

Before generating audio, you need to set up your API credentials:

1. **Click** "API Settings" button in the app
2. **Enter your credentials**:
   - **PlayHT API Key**: Your PlayHT API key
   - **PlayHT User ID**: Your PlayHT user ID
   - **ElevenLabs API Key**: Your ElevenLabs API key
3. **Click** "Save Credentials"

> **Note**: Credentials are stored locally in your browser and are not shared.

### Getting API Keys

- **PlayHT**: Sign up at [play.ht](https://play.ht) and get your API key from the dashboard
- **ElevenLabs**: Sign up at [elevenlabs.io](https://elevenlabs.io) and get your API key from settings

## 🎯 How to Use

### Playing Existing Audio

1. **Select a string** in the Crowdin editor
2. **Click** "🎵 Play Current Audio"
3. The app will:
   - Detect the current language
   - Find the corresponding audio file from the Levante GCP bucket
   - Play the audio automatically

### Generating New Audio

1. **Select a string** with a translation in the Crowdin editor
2. **Click** "🎤 Generate New Audio"
3. **Select a service**: PlayHT or ElevenLabs
4. **Choose a voice** from the dropdown (filtered by current language)
5. **Click** "Generate" to create and play the audio

### Language Detection

The app automatically detects the current language from:
- Crowdin's translation context
- URL parameters
- Falls back to English if detection fails

Voices are automatically filtered to match the detected language.

## ✨ Features

### 🎵 Audio Playback
- **GCP bucket integration**: Retrieves audio files from Google Cloud Platform storage
- **Multi-language support**: Works with French, Spanish, English, and more
- **Direct file access**: Uses string identifiers to access audio files directly

### 🎤 Audio Generation
- **Two TTS services**: PlayHT and ElevenLabs integration
- **Voice filtering**: Shows only voices for the current language
- **Personal voice libraries**: ElevenLabs shows only your custom voices
- **Real-time generation**: Generate and play audio instantly

### 🌍 Language Intelligence
- **Auto-detection**: Recognizes fr-CA, es-MX, en-US, etc.
- **Language mapping**: Maps regional codes to standard languages
- **Voice filtering**: Shows French voices for French content, etc.

### 💾 Credential Management
- **Secure storage**: API keys stored locally in your browser
- **Easy setup**: Simple form to enter and save credentials
- **Recovery options**: Backup and restore credential functionality

## 🔧 Troubleshooting

### "No item ID found" Error

**Problem**: App shows "No item ID found" even when you've selected a string.

**Solutions**:
1. **Click** "🔄 Refresh Context" to force re-sync
2. **Select a different string** then re-select your target string
3. **Refresh the page** and try again
4. **Ensure** the string has a proper identifier (not just free text)

### No Audio Playing from GCP Bucket

**Problem**: "Play Current Audio" doesn't find or play audio from cloud storage.

**Solutions**:
1. **Check the console** for detailed error messages
2. **Verify** the string has an identifier that matches files in the GCP bucket
3. **Ensure** you're working with a supported language
4. **Check** that audio files exist for your item ID in the format: `{language}/{itemId}.mp3`

### No Voices in Dropdown

**Problem**: Service dropdown loads but no voices appear.

**Solutions**:
1. **Check credentials**: Click "API Settings" and verify your API keys
2. **Check console logs**: Look for API errors
3. **For ElevenLabs**: Ensure you have personal voices (not just public ones)
4. **For PlayHT**: Voice library should load from CSV automatically

### Generate Button Stays Disabled

**Problem**: Generate button remains grayed out after selecting a voice.

**Solutions**:
1. **Select both service and voice** in the correct order
2. **Clear selection** and try again: Service → Voice → Generate
3. **Check console** for JavaScript errors

### Language Detection Issues

**Problem**: Wrong language detected or voices filtered incorrectly.

**Solutions**:
1. **Check URL**: Ensure you're in the correct language view in Crowdin
2. **Use Refresh Context**: Force the app to re-detect language
3. **Check console logs**: Look for language detection debug messages

## ❓ FAQ

### Q: Do I need both PlayHT and ElevenLabs?
**A**: No, you can use either service. Configure credentials for the service(s) you want to use.

### Q: Are my API keys secure?
**A**: Yes, API keys are stored locally in your browser only. They're never sent to our servers.

### Q: Can I use this with any Crowdin project?
**A**: Yes, install the app in any project where you have admin permissions.

### Q: Why do I only see some ElevenLabs voices?
**A**: The app only shows your personal voice library (cloned, professional, generated voices), not public voices.

### Q: What audio formats are supported?
**A**: The app generates and plays MP3 audio files.

### Q: Can I use this offline?
**A**: No, the app requires internet connection for TTS services and GCP bucket access.

### Q: What languages are supported?
**A**: All languages supported by PlayHT and ElevenLabs, with intelligent voice filtering for French, Spanish, English, German, Portuguese, Dutch, and more.

### Q: How are audio files stored?
**A**: Existing audio files are stored in Google Cloud Platform storage buckets with the structure: `{language}/{itemId}.mp3`

## 🐛 Report Issues

If you encounter issues:

1. **Check the browser console** for error messages
2. **Try the troubleshooting steps** above
3. **Use the Refresh Context button** to force re-sync
4. **Report persistent issues** with console logs and steps to reproduce

## 📝 Notes

- Voice filtering works best with properly configured language codes in Crowdin
- Audio file lookup uses string identifiers, so ensure your strings have proper IDs
- The app works in all Crowdin editor modes: translate, comfortable, side-by-side, multilingual
- Generated audio is played immediately but not automatically saved to your project
- Existing audio files are retrieved from Google Cloud Platform storage

---

**Version**: 2.0  
**Last Updated**: January 2025  
**Support**: Check console logs for detailed debugging information 