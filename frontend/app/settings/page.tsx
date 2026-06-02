import { SettingsView } from "@/components/settings-view";
import { getSystemSettings } from "@/lib/api";

export default async function SettingsPage() {
  const settings = await getSystemSettings();
  return <SettingsView settings={settings} />;
}
