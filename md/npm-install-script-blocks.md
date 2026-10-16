# npm Install Script Blocks

npm may block dependency install-time scripts such as `preinstall`, `install`, and `postinstall`. Packages that need those scripts can install incompletely. For example, OpenCode's Windows launcher may remain a placeholder if its required postinstall script does not run.

## Allow every package script for this Windows user

To stop npm from asking about blocked package scripts across global and project installs for this user, run this in PowerShell:

```powershell
npm config set dangerously-allow-all-scripts true --location=user
```

This is a broad security tradeoff: it allows install scripts from every package, including transitive dependencies and packages you install in the future. npm calls this an escape hatch and discourages routine use. Only choose it if you are comfortable trusting all installed packages to execute code during installation.

Check the setting with:

```powershell
npm config get dangerously-allow-all-scripts
```

Turn it off again with:

```powershell
npm config delete dangerously-allow-all-scripts --location=user
```

## Safer option: approve trusted packages

For global installs and one-off `npx`/`npm exec` use, maintain a user-level allowlist of package names whose install scripts you trust. For example:

```powershell
npm config set allow-scripts=@opencode/cli --location=user
```

The allowlist is a comma-separated value. To add more packages, include the existing approved names in the new value, for example:

```powershell
npm config set allow-scripts='@opencode/cli,sharp,esbuild' --location=user
```

Use package identities shown by npm's warning. Avoid approving a package just to silence the warning if you do not know why it needs an install script.

For a project, approve scripts in that project's dependency policy rather than relying on a global setting. npm provides `npm approve-scripts`; check `npm help approve-scripts` for the options supported by your installed npm version.

## Repair a package installed while its script was blocked

Changing the policy does not retroactively run scripts for packages already installed. After approving the package or enabling the broad setting, reinstall the affected package. For OpenCode:

```powershell
npm install -g @opencode/cli
```

If a global install using only `--allow-scripts=<package>` fails with `Cannot destructure property 'name' of '.for' as it is undefined`, include the package spec in the same command:

```powershell
npm install -g --allow-scripts=@opencode/cli @opencode/cli
```

## References

- [npm configuration: `allow-scripts`](https://docs.npmjs.com/cli/using-npm/config/#allow-scripts)
- [npm configuration: `dangerously-allow-all-scripts`](https://docs.npmjs.com/cli/using-npm/config/#dangerously-allow-all-scripts)
- [npm `approve-scripts` command](https://docs.npmjs.com/cli/v11/commands/npm-approve-scripts/)
