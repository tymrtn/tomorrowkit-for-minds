# Security

Tomorrowkit is a local app intended to run inside a Minds workspace.

- It binds to `127.0.0.1` by default.
- It has no built-in authentication or authorization layer.
- Matter records are stored as plaintext JSON on the local filesystem.
- Exported archives can contain confidential invention information.
- The application does not send matter data to an AI provider or external API.

Do not expose the Flask server directly to a public or untrusted network. Use
the Minds service proxy and the host's access controls. Protect the data
directory and exported archives with appropriate device encryption, backups,
and filesystem permissions.

Please report suspected vulnerabilities privately to the repository owner
rather than opening a public issue containing confidential material.
