import { dandiApiRoot } from '@/rest';

interface InstanceIdentity {
  isProduction: boolean;
  instanceUrl?: string | null;
}

/**
 * A URL for a dandiset that the DANDI CLI can resolve.
 *
 * Deliberately not derived from `window.location.origin`: the page isn't necessarily
 * served from the instance it talks to (a static PR preview on GitHub Pages runs
 * against the sandbox API, for example), and the CLI has to be pointed at the
 * instance that actually holds the data.
 *
 * Pass an empty `version` for the most recent published version.
 */
function dandisetCliUrl(
  identifier: string,
  version: string,
  { isProduction, instanceUrl }: InstanceIdentity,
): string {
  const versionPath = version ? `/${version}` : '';

  // Use the special 'DANDI:' url prefix if the dandiset lives on the production
  // instance, since that is the instance the CLI resolves those IDs against.
  if (isProduction) {
    return `DANDI:${identifier}${versionPath}`;
  }

  // Otherwise prefer the web URL the instance reports for itself.
  if (instanceUrl) {
    return `${instanceUrl.replace(/\/+$/, '')}/dandiset/${identifier}${versionPath}`;
  }

  // Failing that, address the API directly; the CLI accepts that form too.
  return `${dandiApiRoot}dandisets/${identifier}/${version ? `versions/${version}/` : ''}`;
}

function dandisetDownloadCommand(
  identifier: string,
  version: string,
  instance: InstanceIdentity,
): string {
  return `dandi download ${dandisetCliUrl(identifier, version, instance)}`;
}

export { dandisetCliUrl, dandisetDownloadCommand };
