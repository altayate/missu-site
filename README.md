# Miss-U website

Public support and legal website for Miss-U, operated by Altay Ateşyakan.

This directory is self-contained. Publish **only this directory**, not the parent iOS app repository.

## Build and preview

No packages, frameworks, external fonts, scripts, or cookies are required. Python 3.9+ builds the static pages:

```sh
python3 build.py
python3 build.py --check
python3 -m http.server 8080 --directory docs
```

Open http://localhost:8080. Update page copy in `content/`, styling in `assets/style.css`, and developer/contact/site details in `site.json`. Rebuild and commit `docs/` with source changes. Update the effective date when legal content changes.

## GitHub Pages

Repository: `altayate/missu-site` (public). Serve the `docs` folder from the `main` branch, with HTTPS enforced. The generated `.nojekyll` file avoids a Jekyll build; all assets use project-site-safe URLs. A GitHub Actions workflow checks that generated pages match the source and that local links work.

`domain/` is the separate source for `altayate/altayate.github.io`, served from `main:/`. It publishes https://altayate.github.io/app-ads.txt and redirects the domain home page to the Miss-U website. AdMob discovers the seller file at the hostname root, not under `/missu-site/`; keep that file in the separate domain repository when updating it. Its publisher ID matches the app's configured AdMob publisher.

```sh
gh repo create altayate/missu-site --public --source . --remote origin --push
gh api --method POST repos/altayate/missu-site/pages -f 'source[branch]=main' -f 'source[path]=/docs'
gh api --method PUT repos/altayate/missu-site/pages -F https_enforced=true
```

## App Store links

- Website: https://altayate.github.io/missu-site/
- Privacy: https://altayate.github.io/missu-site/privacy/
- Terms: https://altayate.github.io/missu-site/terms/
- Support: https://altayate.github.io/missu-site/support/
- Deletion instructions: https://altayate.github.io/missu-site/delete-account/
- Software license: Apple's Standard EULA, https://www.apple.com/legal/internet-services/itunes/dev/stdeula/

The service terms supplement Apple's Standard EULA; they are not a separately submitted custom software EULA. Set the app's `MissUPrivacyPolicyURL` and `MissUTermsOfUseURL` only after verifying the live pages. Publishing these pages does not activate purchases, live ads, reconnect enforcement, or canvas resets.

The English policy follows the app's source and rollout notes, updated on 14 November 2026 for production non-personalized ads and Google UMP privacy controls. It also covers Firebase telemetry, photo encryption limitations, Daily UTC expiry, disconnect cleanup, seven-day file recovery, test advertising, and conditional future Premium/reconnect/canvas behavior. Keep these disclosures synchronized with releases and provider configuration. Provider retention settings and required international transfer arrangements must reflect actual operations.

Sources checked when drafting: [Apple review guidelines](https://developer.apple.com/app-store/review/guidelines/), [Apple Standard EULA](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/), [Firebase privacy](https://firebase.google.com/support/privacy), [AdMob data disclosures](https://developers.google.com/admob/ios/privacy/data-disclosure), [GitHub privacy](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).
