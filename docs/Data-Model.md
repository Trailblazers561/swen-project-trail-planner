# Data Model
It is the opinion of the 2025-2026 Trailblazers software engineering team that the data model is the core of the application. A freeze on the data model was placed on 4/5/2026, and it is the intention of the team that no more major changes to the existing data model be made. Thus, if you are reading this as a team in the future looking to improve on our changes, its advised that you simply make additions and enhancements to the existing model.

## Reasoning behind the Model
The model we went with is the result of a total redesign from a previous team, that we spent weeks researching, evaluating, and perfecting. It is performant, maintainable, and extensible for your usage. Many unnecessary fields have been included for you, as we believe they might be handy in the evolution of the system towards a full train network management system.

We made sure to structure our tables in a format best suited to the platform - DynamoDb (NoSQL, nonrelational). This means embracing some slight redundancy in the name of higher performance. Details can be found in our research documents on the shared drive.