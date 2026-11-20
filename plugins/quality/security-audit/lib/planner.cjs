'use strict';

const fs = require('node:fs');
const path = require('node:path');

const DEFAULT_LIMITS = Object.freeze({
  maxFiles: 50000,
  maxDirectories: 10000,
  maxDepth: 40,
  maxBytes: 512 * 1024 * 1024,
});
const EXCLUDED_DIRECTORIES = Object.freeze([
  '.git', '.hg', '.svn', 'node_modules', 'vendor', '.venv', 'venv',
  '__pycache__', 'dist', 'build', '.terraform', '.next', 'coverage',
]);
const UNSAFE_NAME = /[\p{Cc}\p{Cf}\p{Cs}\p{Zl}\p{Zp}\p{Default_Ignorable_Code_Point}\\]/u;
const CONTROL_CHARACTER = /[\p{Cc}\p{Cf}\p{Cs}\p{Zl}\p{Zp}\p{Default_Ignorable_Code_Point}]/u;
const ECOSYSTEM_FILES = new Map([
  ['package.json', 'javascript'], ['package-lock.json', 'javascript'],
  ['npm-shrinkwrap.json', 'javascript'], ['yarn.lock', 'javascript'],
  ['pnpm-lock.yaml', 'javascript'], ['bun.lock', 'javascript'], ['bun.lockb', 'javascript'],
  ['pyproject.toml', 'python'], ['requirements.txt', 'python'],
  ['Pipfile', 'python'], ['Pipfile.lock', 'python'], ['poetry.lock', 'python'],
  ['uv.lock', 'python'], ['setup.py', 'python'], ['setup.cfg', 'python'],
  ['go.mod', 'go'], ['go.sum', 'go'],
  ['Cargo.toml', 'rust'], ['Cargo.lock', 'rust'],
  ['pom.xml', 'java'], ['build.gradle', 'java'], ['build.gradle.kts', 'java'],
  ['gradle.lockfile', 'java'], ['packages.lock.json', 'dotnet'],
  ['packages.config', 'dotnet'], ['Gemfile', 'ruby'], ['Gemfile.lock', 'ruby'],
  ['composer.json', 'php'], ['composer.lock', 'php'],
]);

function fail(message) { throw new Error(message); }

function limitsFrom(options) {
  const limits = {};
  for (const [key, defaultValue] of Object.entries(DEFAULT_LIMITS)) {
    const value = options[key] ?? defaultValue;
    if (!Number.isSafeInteger(value) || value < 1 || value > defaultValue) {
      fail(`Invalid ${key}: use a positive integer no greater than ${defaultValue}`);
    }
    limits[key] = value;
  }
  return limits;
}

function checkedRoot(target) {
  if (typeof target !== 'string' || !target.trim() || CONTROL_CHARACTER.test(target)
    || (path.sep !== '\\' && target.includes('\\'))) {
    fail('Target must be a nonempty local directory path without control characters');
  }
  const absolute = path.resolve(target);
  const parsed = path.parse(absolute);
  let current = parsed.root;
  const segments = absolute.slice(parsed.root.length).split(path.sep).filter(Boolean);
  try {
    // Check each ancestor, not only the final directory. Never intentionally
    // traverse a symlink to inventory a different repository.
    for (const segment of segments) {
      current = path.join(current, segment);
      const stat = fs.lstatSync(current);
      if (stat.isSymbolicLink()) fail('Target and its ancestors must not be symlinks');
      if (!stat.isDirectory()) fail('Target and its ancestors must be directories');
    }
    if (!fs.lstatSync(absolute).isDirectory()) fail('Target must be a directory');
  } catch (error) {
    if (error.code) fail('Target could not be opened as a local directory');
    throw error;
  }
  return absolute;
}

function detectMarker(relative) {
  const base = path.posix.basename(relative);
  const markers = [];
  const ecosystem = ECOSYSTEM_FILES.get(base);
  if (ecosystem) markers.push({ category: 'dependencies', ecosystem, path: relative });
  else if (/\.(?:csproj|fsproj|vbproj)$/i.test(base)) {
    markers.push({ category: 'dependencies', ecosystem: 'dotnet', path: relative });
  } else if (/^requirements(?:[.-][\w-]+)?\.txt$/i.test(base)) {
    markers.push({ category: 'dependencies', ecosystem: 'python', path: relative });
  }
  if (/^(?:Dockerfile|Containerfile)(?:\.[\w.-]+)?$/i.test(base)
    || /^(?:docker-)?compose(?:\.[\w.-]+)?\.ya?ml$/i.test(base)) {
    markers.push({ category: 'containers', ecosystem: null, path: relative });
  }
  if (/\.(?:tf|tfvars|bicep)$/i.test(base)
    || /^(?:Chart\.yaml|kustomization\.ya?ml|serverless\.ya?ml|cdk\.json|Pulumi\.ya?ml)$/i.test(base)) {
    markers.push({ category: 'infrastructure', ecosystem: null, path: relative });
  }
  if (/(?:^|\/)\.github\/workflows\/[^/]+\.ya?ml$/i.test(relative)) {
    markers.push({ category: 'github-actions', ecosystem: null, path: relative });
  }
  if (/^(?:AGENTS\.md|CLAUDE\.md|mcp\.json|\.mcp\.json|langgraph\.json)$/i.test(base)
    || /(?:^|\/)(?:\.claude|\.cursor|\.codex)\//.test(relative)) {
    markers.push({ category: 'agent-configuration', ecosystem: null, path: relative });
  }
  return markers;
}

function inventoryRepository(root, limits) {
  const stack = [{ absolute: root, relative: '', depth: 0 }];
  const omissions = new Set();
  const markers = [];
  const excluded = new Set(EXCLUDED_DIRECTORIES);
  const counts = { files: 0, directories: 0, entries: 0, bytes: 0, symlinks_skipped: 0, excluded_directories: 0 };
  let stop = false;
  while (stack.length && !stop) {
    const directory = stack.pop();
    if (counts.directories >= limits.maxDirectories) {
      omissions.add('directory_limit_reached');
      break;
    }
    let before;
    let entries;
    try {
      before = fs.lstatSync(directory.absolute);
      if (before.isSymbolicLink() || !before.isDirectory()) {
        omissions.add('directory_changed_during_inventory');
        continue;
      }
      const resolved = fs.realpathSync(directory.absolute);
      const relativeResolved = path.relative(root, resolved);
      if (relativeResolved === '..' || relativeResolved.startsWith('..' + path.sep) || path.isAbsolute(relativeResolved)) {
        omissions.add('directory_left_target');
        continue;
      }
      // Directory names only: no source file contents or project code are read.
      // Limit enumeration before sorting to avoid unbounded arrays in huge dirs.
      entries = [];
      const handle = fs.opendirSync(directory.absolute);
      try {
        let entry;
        const maxEntries = limits.maxFiles + limits.maxDirectories;
        while ((entry = handle.readSync()) !== null) {
          if (counts.entries >= maxEntries) {
            omissions.add('directory_entry_limit_reached');
            stop = true;
            break;
          }
          entries.push(entry.name);
          counts.entries++;
        }
      } finally {
        handle.closeSync();
      }
      const after = fs.lstatSync(directory.absolute);
      if (!after.isDirectory() || after.isSymbolicLink()
        || before.dev !== after.dev || before.ino !== after.ino) {
        omissions.add('directory_changed_during_inventory');
        continue;
      }
    } catch {
      omissions.add('directory_unreadable_or_changed');
      continue;
    }
    counts.directories++;
    entries.sort();
    const children = [];
    for (const name of entries) {
      if (UNSAFE_NAME.test(name)) {
        omissions.add('unsupported_filename_skipped');
        continue;
      }
      const absolute = path.join(directory.absolute, name);
      const relative = directory.relative ? `${directory.relative}/${name}` : name;
      let stat;
      try { stat = fs.lstatSync(absolute); } catch {
        omissions.add('entry_unreadable_or_changed');
        continue;
      }
      if (stat.isSymbolicLink()) {
        counts.symlinks_skipped++;
        omissions.add('symlinks_not_followed');
        continue;
      }
      if (stat.isDirectory()) {
        if (excluded.has(name)) {
          counts.excluded_directories++;
        } else if (directory.depth >= limits.maxDepth) {
          omissions.add('depth_limit_reached');
        } else if (counts.directories + stack.length + children.length >= limits.maxDirectories) {
          omissions.add('directory_limit_reached');
        } else {
          children.push({ absolute, relative, depth: directory.depth + 1 });
        }
        continue;
      }
      if (!stat.isFile()) {
        omissions.add('nonregular_entries_skipped');
        continue;
      }
      if (counts.files >= limits.maxFiles) {
        omissions.add('file_limit_reached');
        stop = true;
        break;
      }
      if (!Number.isSafeInteger(stat.size) || stat.size > limits.maxBytes - counts.bytes) {
        omissions.add('inventory_byte_limit_reached');
        stop = true;
        break;
      }
      counts.files++;
      counts.bytes += stat.size;
      markers.push(...detectMarker(relative));
    }
    // Reverse push retains lexical traversal order with a LIFO worklist.
    stack.push(...children.reverse());
  }
  markers.sort((a, b) => a.path.localeCompare(b.path, 'en') || a.category.localeCompare(b.category, 'en'));
  return {
    complete: omissions.size === 0,
    counts,
    ecosystems: [...new Set(markers.map(m => m.ecosystem).filter(Boolean))].sort(),
    markers,
    omissions: [...omissions].sort(),
    excluded_directory_names: [...EXCLUDED_DIRECTORIES],
    limits,
    byte_count_meaning: 'Sum of inventoried regular-file sizes; file contents are not read.',
  };
}

function recipe(id, domain, argv, extra = {}) {
  return {
    id, domain, argv,
    executable: argv[0],
    execution_status: 'not_run',
    needs_configuration: argv.some(argument => /<[^>]+>/.test(argument)),
    network_policy: 'deny_external_network',
    prerequisites: [
      'Install and verify the scanner separately; the planner does not install or execute tools.',
      'Run in the audit workflow sandbox with read-only source, resource limits, and an allowlisted environment.',
      'Resolve placeholders to trusted paths; output must be outside the target repository.',
      'Inspect scanner configuration and ignore rules; record omitted files and disabled checks.',
    ],
    ...extra,
  };
}

function scanRecipes(root, profile, inventory) {
  const categories = new Set(inventory.markers.map(marker => marker.category));
  const scans = [
    recipe('semgrep', 'source-analysis', [
      'semgrep', 'scan', '--config', '<trusted-local-rules.yml>', '--metrics', 'off',
      '--disable-version-check', '--json', '--output', '<output-dir>/semgrep.json', root,
    ], {
      import_format: 'semgrep',
      output: '<output-dir>/semgrep.json',
      exit_codes: { '0': 'Scan completed; inspect results and errors, not exit status alone.', 'other': 'Operational failure or explicit scanner policy failure; inspect output before import.' },
      limitations: ['Local rules are required; registry rules and cloud login are not used.', 'Ruleset coverage and language support must be recorded; a successful run is not proof of full coverage.'],
      source: 'https://docs.semgrep.dev/cli-reference',
    }),
    recipe('gitleaks', 'secrets', [
      'gitleaks', 'dir', root, '--redact=100', '--report-format', 'json',
      '--report-path', '<output-dir>/gitleaks.json',
    ], {
      import_format: 'gitleaks',
      output: '<output-dir>/gitleaks.json',
      exit_codes: { '0': 'No leaks reported.', '1': 'Leaks found by default; check stderr because configuration/runtime errors can also fail.', 'other': 'Operational failure; do not treat as a clean scan.' },
      limitations: ['Directory mode inspects the working tree, not Git history.', 'Redaction reduces report exposure; do not print raw scanner logs or upload reports.'],
      source: 'https://github.com/gitleaks/gitleaks',
    }),
  ];
  if (categories.has('dependencies')) {
    scans.push(recipe('osv', 'dependency-vulnerabilities', [
      'osv-scanner', 'scan', 'source', '--recursive', '--format', 'json', '--output-file',
      '<output-dir>/osv.json', '--offline', '--no-call-analysis=go,rust', '--no-resolve', root,
    ], {
      import_format: 'osv',
      output: '<output-dir>/osv.json',
      exit_codes: { '0': 'No known vulnerabilities reported.', '1': 'Vulnerabilities reported.', 'other': 'Operational failure; inspect command errors and cache availability.' },
      prerequisites: [
        'Use a verified OSV-Scanner v2 binary and pre-provisioned advisory cache for the detected ecosystems.',
        'Use the audit sandbox with denied external networking, resource limits, read-only source and an allowlisted environment.',
        'Resolve output placeholders outside the target and verify scanner configuration.',
      ],
      limitations: ['Missing or stale offline advisory data leaves dependency coverage incomplete.', 'No dependency resolution or call analysis is performed; missing lockfiles and transitive dependencies remain gaps.'],
      connected_alternative: {
        execution: 'manual_explicit_opt_in_only',
        description: 'A separately authorized connected scan may refresh advisory data; plan its permitted destinations and data exposure first.',
        possible_egress: ['Package names, versions and dependency identifiers sent to advisory services.', 'Requests to package registries if resolution is separately enabled.'],
      },
      source: 'https://github.com/google/osv-scanner',
    }));
  }
  if (profile !== 'quick' && (categories.has('dependencies') || categories.has('containers') || categories.has('infrastructure'))) {
    scans.push(recipe('trivy', 'filesystem-dependencies-and-configuration', [
      'trivy', 'fs', '--scanners', 'vuln,misconfig,secret', '--format', 'json',
      '--output', '<output-dir>/trivy.json', '--offline-scan', '--skip-db-update',
      '--skip-java-db-update', '--skip-check-update', '--skip-version-check', '--disable-telemetry', root,
    ], {
      import_format: 'trivy',
      output: '<output-dir>/trivy.json',
      exit_codes: { '0': 'Scan completed with default exit policy; findings may still exist.', 'other': 'Operational or configured policy failure; inspect output and logs.' },
      prerequisites: [
        'Use a verified current Trivy binary supporting these flags and pre-provisioned vulnerability, Java and misconfiguration caches as applicable.',
        'Use the audit sandbox; flags alone are not network confinement.',
        'Inspect trivy.yaml, ignore rules and secret configuration; resolve outputs outside the target.',
      ],
      limitations: ['Missing offline databases or check bundles are blocked coverage, not a clean scan.', 'Filesystem scans do not inspect a running deployment or prove container runtime hardening.'],
      source: 'https://github.com/aquasecurity/trivy/blob/main/docs/guide/references/configuration/cli/trivy_filesystem.md',
    }));
  }
  if (profile !== 'quick' && categories.has('github-actions')) {
    scans.push(recipe('zizmor', 'github-actions', [
      'zizmor', '--offline', '--format', 'sarif', '--strict-collection', root,
    ], {
      needs_configuration: true,
      import_format: 'sarif',
      output: '<output-dir>/zizmor.sarif',
      capture_stdout_to: '<output-dir>/zizmor.sarif',
      exit_codes: { '0': 'SARIF output completed; findings do not produce a nonzero exit.', '1': 'Runtime error.', '2': 'Argument parse failure.' },
      limitations: ['Capture stdout using the runner API, not shell string interpolation.', 'Offline mode omits audits requiring remote GitHub data.'],
      source: 'https://docs.zizmor.sh/usage/',
    }));
  }
  if (profile === 'deep') {
    scans.push(recipe('syft', 'software-inventory', [
      'syft', '--from', 'dir', root, '-o', 'cyclonedx-json=<output-dir>/sbom.cdx.json',
    ], {
      import_format: null,
      artifact_format: 'cyclonedx-json',
      output: '<output-dir>/sbom.cdx.json',
      environment: { SYFT_CHECK_FOR_APP_UPDATE: 'false' },
      exit_codes: { '0': 'SBOM generation completed; inspect inventory and cataloger coverage.', 'other': 'Operational failure; do not use a partial SBOM as full inventory.' },
      limitations: ['SBOM is an inventory artifact, not a vulnerability or confirmed-finding report.', 'Use a reviewed configuration and deny network access; catalogers and configuration may otherwise fetch remote data.'],
      source: 'https://oss.anchore.com/docs/guides/sbom/scan-targets/',
    }));
  }
  return scans;
}

function planRepository(target, options = {}) {
  if (options === null || typeof options !== 'object' || Array.isArray(options)) fail('Options must be an object');
  const profile = options.profile ?? 'standard';
  if (!['quick', 'standard', 'deep'].includes(profile)) fail('Unknown profile; use quick, standard, or deep');
  const root = checkedRoot(target);
  const limits = limitsFrom(options);
  const inventory = inventoryRepository(root, limits);
  return {
    schema_version: '1.0.0',
    kind: 'scan-plan',
    target: root,
    profile,
    complete: inventory.complete,
    execution_status: 'not_run',
    inventory,
    coverage_limitations: [
      'Complete describes bounded filename inventory only. No scanner has run and no security conclusion has been established.',
      'Excluded directory names and skipped entries are outside this inventory; inspect them separately if relevant.',
      'Detection uses filenames, not manifest contents. Generic Kubernetes or CloudFormation YAML and custom dependency files may require manual additions.',
      'This plan inventories a mutable working directory, not an atomic commit snapshot; use a stable disposable checkout for reproducibility.',
      'Scanner rules and advisory database versions, timestamps, configuration, execution failures and actual reviewed source must be recorded during execution.',
      ...(profile === 'quick' ? ['Quick profile omits infrastructure, GitHub Actions and SBOM recipes even when relevant markers exist.'] : []),
      ...(inventory.markers.some(marker => marker.category === 'agent-configuration')
        ? ['Agent configuration was detected; review prompt injection, tool authority and data exposure with the existing AI-AND-LLM companion. No automated AI security scan is claimed.'] : []),
    ],
    scans: scanRecipes(root, profile, inventory),
  };
}

module.exports = { DEFAULT_LIMITS, EXCLUDED_DIRECTORIES, planRepository };
