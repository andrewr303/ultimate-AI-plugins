import SwiftUI

enum Tool: String, CaseIterable, Identifiable {
    case pen, highlighter, eraser
    var id: String { rawValue }

    var title: String {
        switch self {
        case .pen: "Pen"
        case .highlighter: "Highlighter"
        case .eraser: "Eraser"
        }
    }

    var symbol: String {
        switch self {
        case .pen: "pencil.tip"
        case .highlighter: "highlighter"
        case .eraser: "eraser"
        }
    }
}

@Observable
final class Sketch {
    var strokes: [[CGPoint]] = []
    var undone: [[CGPoint]] = []
    var tool: Tool = .pen

    var canUndo: Bool { !strokes.isEmpty }
    var canRedo: Bool { !undone.isEmpty }

    func undo() { if let last = strokes.popLast() { undone.append(last) } }
    func redo() { if let last = undone.popLast() { strokes.append(last) } }
}

struct CanvasView: View {
    @State private var sketch = Sketch()
    @State private var current: [CGPoint] = []

    var body: some View {
        NavigationStack {
            Canvas { context, _ in
                for stroke in sketch.strokes + [current] where stroke.count > 1 {
                    var path = Path()
                    path.addLines(stroke)
                    context.stroke(path, with: .color(.primary), lineWidth: 3)
                }
            }
            .background(Color(.systemBackground))
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { current.append($0.location) }
                    .onEnded { _ in
                        sketch.strokes.append(current)
                        sketch.undone.removeAll()
                        current = []
                    }
            )
            .navigationTitle("Sketch")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview {
    CanvasView()
}
