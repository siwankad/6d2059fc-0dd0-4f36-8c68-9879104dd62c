FROM mcr.microsoft.com/dotnet/sdk:10.0 AS test
WORKDIR /src
COPY . .
RUN dotnet test max-run.slnx -c Release --settings coverage.runsettings --collect:"XPlat Code Coverage" --results-directory /tmp/coverage

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish src/LongestIncreasingRun.Cli/LongestIncreasingRun.Cli.csproj -c Release -o /app

FROM mcr.microsoft.com/dotnet/runtime:10.0
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "LongestIncreasingRun.Cli.dll"]
