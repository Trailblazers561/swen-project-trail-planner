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

export enum TimeFrame {
  Day = "day",
  Week = "week",
  Fortnight = "fortnight",
  Month = "month"
}