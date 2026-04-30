"""Shared persistent QWebEngineProfile for Google sign-in across screens."""

import os
from PyQt5.QtWebEngineWidgets import (
    QWebEngineProfile,
    QWebEngineSettings,
    QWebEngineScript,
)

_shared_profile = None


def _inject_stealth_script(profile):
    """Hide automation indicators that Google checks for."""
    script = QWebEngineScript()
    script.setName("stealth")
    script.setInjectionPoint(QWebEngineScript.DocumentCreation)
    script.setWorldId(QWebEngineScript.MainWorld)
    script.setRunsOnSubFrames(True)
    script.setSourceCode(
        """
        // Hide webdriver flag
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Fake plugins array (real browsers have plugins)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin'},
                {name: 'Chrome PDF Viewer'},
                {name: 'Native Client'}
            ]
        });

        // Languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });

        // Fake chrome object
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };

        // Fix permissions query (Google checks this)
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications'
                ? Promise.resolve({state: Notification.permission})
                : originalQuery(parameters)
        );

        // Hide that we're headless
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });
        """
    )
    profile.scripts().insert(script)


def get_shared_profile(parent=None):
    """
    Returns a singleton QWebEngineProfile with persistent storage
    and aggressive Chrome spoofing for Google sign-in.
    """
    global _shared_profile

    if _shared_profile is not None:
        return _shared_profile

    profile_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "browser_data",
        "google_profile",
    )
    profile_path = os.path.normpath(profile_path)
    os.makedirs(profile_path, exist_ok=True)

    profile = QWebEngineProfile("google_persistent", parent)
    profile.setPersistentStoragePath(profile_path)
    profile.setCachePath(os.path.join(profile_path, "cache"))
    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.ForcePersistentCookies
    )

    # Latest Chrome UA - no "QtWebEngine" string
    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    settings = profile.settings()
    settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
    settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
    settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
    settings.setAttribute(
        QWebEngineSettings.JavascriptCanOpenWindows, True
    )
    settings.setAttribute(
        QWebEngineSettings.JavascriptCanAccessClipboard, True
    )

    _inject_stealth_script(profile)

    _shared_profile = profile
    return profile