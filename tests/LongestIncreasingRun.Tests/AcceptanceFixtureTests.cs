using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace LongestIncreasingRun.Tests;

/// <summary>
/// The eleven published cases and the eight rule checks. Each test compares
/// the function result with the expected string, and checks that the input
/// bytes still match the recorded SHA-256 digest.
/// </summary>
public sealed class AcceptanceFixtureTests
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
    };

    private static readonly FixtureDocument Fixture = Load();

    public static IEnumerable<object[]> PublishedCaseIds()
    {
        return Fixture.PublishedCases.Select(item => new object[] { item.Id });
    }

    public static IEnumerable<object[]> RuleCheckIds()
    {
        return Fixture.RuleChecks.Select(item => new object[] { item.Id });
    }

    [Theory]
    [MemberData(nameof(PublishedCaseIds))]
    public void PublishedCaseMatchesTheExpectedRun(string id)
    {
        AssertCase(Find(Fixture.PublishedCases, id));
    }

    [Theory]
    [MemberData(nameof(RuleCheckIds))]
    public void RuleCheckMatchesTheExpectedRun(string id)
    {
        AssertCase(Find(Fixture.RuleChecks, id));
    }

    private static void AssertCase(FixtureCase item)
    {
        Assert.Equal(item.Sha256, Sha256Hex(item.Input));
        Assert.Equal(item.Expected, LongestIncreasingRunFinder.Find(item.Input));
    }

    private static FixtureCase Find(IReadOnlyList<FixtureCase> cases, string id)
    {
        FixtureCase? item = cases.FirstOrDefault(candidate => candidate.Id == id);
        Assert.NotNull(item);
        return item;
    }

    private static string Sha256Hex(string value)
    {
        byte[] hash = SHA256.HashData(Encoding.UTF8.GetBytes(value));
        return Convert.ToHexString(hash).ToLowerInvariant();
    }

    private static FixtureDocument Load()
    {
        string path = Path.Combine(AppContext.BaseDirectory, "acceptance-fixtures.json");
        string json = File.ReadAllText(path);
        return JsonSerializer.Deserialize<FixtureDocument>(json, JsonOptions)
            ?? throw new InvalidOperationException("The acceptance fixture file was empty.");
    }

    private sealed class FixtureDocument
    {
        public List<FixtureCase> PublishedCases { get; init; } = [];

        public List<FixtureCase> RuleChecks { get; init; } = [];
    }

    private sealed class FixtureCase
    {
        public string Id { get; init; } = string.Empty;

        public string Input { get; init; } = string.Empty;

        public string Expected { get; init; } = string.Empty;

        public string Sha256 { get; init; } = string.Empty;
    }
}
