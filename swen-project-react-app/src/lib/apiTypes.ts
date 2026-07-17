export enum UserRole {
    RootAdmin = "root_admin",
    Admin = "admin",
    TrailManager = "trail_manager",
    User = "user",
    Guest = "guest"
  }

export enum Granularity {
  Hour = "hour",
  Day = "day",
  Week = "week",
  Month = "month",
  Year = "year"
}

export const GranularityText: Record<Granularity, string> = {
  [Granularity.Hour]: "Hourly",
  [Granularity.Day]: "Daily",
  [Granularity.Week]: "Weekly",
  [Granularity.Month]: "Monthly",
  [Granularity.Year]: "Yearly"
};

export enum HeatmapAlgorithm {
  Absolute = "absolute",
  Relative = "relative"
}

export enum DeviceLogType {
  Unknown = "unknown",
  DataUpload = "data_upload",
  ConnectivityTest = "device_info_connectivity_test",
  CertificateRegistration = "device_certificate_registration",
  CertificateRenewal = "device_certificate_renewal"
}

export const DeviceLogMap: Record<DeviceLogType, string> = {
  [DeviceLogType.Unknown]: "Unknown",
  [DeviceLogType.DataUpload]: "Data Upload",
  [DeviceLogType.ConnectivityTest]: "Connectivity Test",
  [DeviceLogType.CertificateRegistration]: "Certificate Registration",
  [DeviceLogType.CertificateRenewal]: "Certificate Renewal"
};