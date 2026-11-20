import Foundation

// A source-reviewed wire-shape fragment, not a standalone compiled application.
// Add these types to the actual client target and verify its compiler/SDK.
struct ContractItem: Codable, Equatable, Sendable {
    let id: String
    let title: String
    // Preserve the UTC wire text here; parse at a deliberate domain boundary.
    let createdAt: String
    let revision: String
}

struct CreateContractItem: Encodable, Sendable {
    let title: String
}

struct ContractFailure: Codable, Equatable, Sendable {
    struct Detail: Codable, Equatable, Sendable {
        let code: String
        let message: String
    }
    let error: Detail
    let requestId: String
}

// Example target-test fragment to adapt, not an execution result:
// let bytes = try Data(contentsOf: fixtureURL)
// let item = try JSONDecoder().decode(ContractItem.self, from: bytes)
// XCTAssertEqual(item.title, "Café 🚀")
// XCTAssertEqual(item.createdAt, "2026-10-26T00:00:00.000Z")
// Validate a proposed title with title.unicodeScalars.count <= 80, not String.count
// (grapheme clusters) or UTF-16 code-unit count. The server validates again.
