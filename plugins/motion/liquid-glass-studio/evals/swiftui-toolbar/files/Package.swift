// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "Sketchpad",
    platforms: [.iOS(.v17)],
    products: [.library(name: "Sketchpad", targets: ["Sketchpad"])],
    targets: [.target(name: "Sketchpad")]
)
