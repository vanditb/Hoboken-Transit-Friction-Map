# macOS Collector Setup

The optional LaunchAgent template is at `scripts/macos/com.vandit.hoboken-friction-collector.plist.example`. It runs one collector snapshot every 15 minutes after you copy and customize it.

Before using it, check that the Python path and project path in the template match your Mac. The template uses `/usr/bin/python3`, but a virtual environment may use a different Python executable.

To set it up manually:

```bash
cp scripts/macos/com.vandit.hoboken-friction-collector.plist.example ~/Library/LaunchAgents/com.vandit.hoboken-friction-collector.plist
launchctl load ~/Library/LaunchAgents/com.vandit.hoboken-friction-collector.plist
```

To stop it later:

```bash
launchctl unload ~/Library/LaunchAgents/com.vandit.hoboken-friction-collector.plist
```

This is optional and is not installed automatically by the project. The Mac still needs to be awake and have internet access for a scheduled collection to work.
