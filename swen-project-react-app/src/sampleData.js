const sampleData = [
    { Location: "WolfJaw Peak", Timestamp: "2025-02-08T18:30:00Z" },
    { Location: "WolfJaw Peak", Timestamp: "2025-02-04T12:00:00Z" },
    { Location: "WolfJaw Peak", Timestamp: "2025-02-04T15:00:00Z" },
    { Location: "WolfJaw Peak", Timestamp: "2025-02-12T05:15:00Z" },
    { Location: "AlgonquinPeak", Timestamp: "2025-02-20T14:00:00Z" },
    { Location: "AlgonquinPeak", Timestamp: "2025-02-24T07:20:00Z" },
    { Location: "AlgonquinPeak", Timestamp: "2025-02-27T19:10:00Z" },
    { Location: "Mount Marcy", Timestamp: "2025-03-03T02:50:00Z" },
    { Location: "Mount Marcy", Timestamp: "2025-02-02T17:45:00Z" },
    { Location: "WolfJaw Peak", Timestamp: "2025-02-03T14:15:00Z" },
    { Location: "WolfJaw Peak", Timestamp: "2025-02-03T16:00:00Z" },
    { Location: "AlgonquinPeak", Timestamp: "2025-02-03T19:30:00Z" },
    { Location: "Mount Marcy", Timestamp: "2025-02-04T20:15:00Z" },
    { Location: "Mount Marcy", Timestamp: "2025-02-04T22:30:00Z" },
  ];
  
  // Generate 150+ additional sample points with duplicate timestamps
  const locations = ["WolfJaw Peak", "AlgonquinPeak", "Mount Marcy", "Cascade Mountain", "Giant Mountain"];
  const startDate = new Date("2025-02-01T00:00:00Z");
  const endDate = new Date("2025-03-15T23:59:59Z");
  
  for (let i = 0; i < 150; i++) {
    const randomLocation = locations[Math.floor(Math.random() * locations.length)];
  
    // Generate a random date within the range
    const randomDate = new Date(
      startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime())
    );
  
    // Keep the time fixed for some data points to create duplicates
    if (Math.random() > 0.5) {
      randomDate.setHours(8, 30, 0, 0); // 8:30 AM duplicates
    } else if (Math.random() > 0.3) {
      randomDate.setHours(14, 0, 0, 0); // 2:00 PM duplicates
    } else {
      randomDate.setMinutes(Math.floor(Math.random() * 60)); // Randomize minutes
    }
  
    sampleData.push({ Location: randomLocation, Timestamp: randomDate.toISOString() });
  }
  
  export default sampleData;
  