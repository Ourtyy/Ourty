// Renders a 1000x1500 Pinterest pin: photo on top, cream panel with category + title + brand.
// Usage: swift tools/make_pin.swift <photo path or URL> <category label> <title> <output.png>
import AppKit

let args = CommandLine.arguments
guard args.count == 5 else {
    print("usage: make_pin.swift <photo> <category> <title> <out.png>")
    exit(1)
}
let (photoArg, category, title, outPath) = (args[1], args[2].uppercased(), args[3], args[4])

let W: CGFloat = 1000, H: CGFloat = 1500
let photoH: CGFloat = 900
let cream = NSColor(calibratedRed: 0.984, green: 0.980, blue: 0.969, alpha: 1)
let green = NSColor(calibratedRed: 0.184, green: 0.478, blue: 0.341, alpha: 1)
let ink = NSColor(calibratedRed: 0.122, green: 0.165, blue: 0.141, alpha: 1)
let muted = NSColor(calibratedRed: 0.373, green: 0.420, blue: 0.392, alpha: 1)

func loadImage(_ s: String) -> NSImage? {
    if s.hasPrefix("http"), let url = URL(string: s), let data = try? Data(contentsOf: url) { return NSImage(data: data) }
    return NSImage(contentsOfFile: s)
}
guard let photo = loadImage(photoArg) else { print("could not load photo"); exit(1) }

guard let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(W), pixelsHigh: Int(H), bitsPerSample: 8,
                                 samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                                 bytesPerRow: 0, bitsPerPixel: 0) else { exit(1) }
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)

// background
cream.setFill()
NSRect(x: 0, y: 0, width: W, height: H).fill()

// photo, cover-cropped into the top area (AppKit origin is bottom-left)
let photoRect = NSRect(x: 0, y: H - photoH, width: W, height: photoH)
let ps = photo.size
let scale = max(photoRect.width / ps.width, photoRect.height / ps.height)
let srcW = photoRect.width / scale, srcH = photoRect.height / scale
let src = NSRect(x: (ps.width - srcW) / 2, y: (ps.height - srcH) / 2, width: srcW, height: srcH)
photo.draw(in: photoRect, from: src, operation: .copy, fraction: 1)

// soft curved edge between photo and panel
let curve = NSBezierPath()
curve.move(to: NSPoint(x: 0, y: H - photoH + 40))
curve.curve(to: NSPoint(x: W, y: H - photoH + 40), controlPoint1: NSPoint(x: W * 0.3, y: H - photoH - 20),
            controlPoint2: NSPoint(x: W * 0.7, y: H - photoH - 20))
curve.line(to: NSPoint(x: W, y: 0))
curve.line(to: NSPoint(x: 0, y: 0))
curve.close()
cream.setFill()
curve.fill()

func font(_ names: [String], _ size: CGFloat, bold: Bool = false) -> NSFont {
    for n in names { if let f = NSFont(name: n, size: size) { return f } }
    return bold ? NSFont.boldSystemFont(ofSize: size) : NSFont.systemFont(ofSize: size)
}
let center = NSMutableParagraphStyle()
center.alignment = .center
center.lineBreakMode = .byWordWrapping

// category pill
let catAttrs: [NSAttributedString.Key: Any] = [
    .font: font(["AvenirNext-DemiBold", "Avenir-Heavy"], 26), .foregroundColor: NSColor.white,
    .kern: 3.0, .paragraphStyle: center]
let catSize = (category as NSString).size(withAttributes: catAttrs)
let pill = NSRect(x: (W - catSize.width - 56) / 2, y: H - photoH - 10, width: catSize.width + 56, height: 52)
green.setFill()
NSBezierPath(roundedRect: pill, xRadius: 26, yRadius: 26).fill()
(category as NSString).draw(in: NSRect(x: pill.minX, y: pill.minY + (52 - catSize.height) / 2, width: pill.width, height: catSize.height),
                            withAttributes: catAttrs)

// title: shrink until it fits
let titleBox = NSRect(x: 80, y: 190, width: W - 160, height: H - photoH - 250)
var size: CGFloat = 76
var tAttrs: [NSAttributedString.Key: Any] = [:]
var tRect = NSRect.zero
repeat {
    tAttrs = [.font: font(["NewYorkLarge-Bold", "NewYork-Bold", "Georgia-Bold"], size, bold: true),
              .foregroundColor: ink, .paragraphStyle: center]
    tRect = (title as NSString).boundingRect(with: NSSize(width: titleBox.width, height: 2000),
                                             options: [.usesLineFragmentOrigin], attributes: tAttrs)
    size -= 2
} while tRect.height > titleBox.height && size > 36
let ty = titleBox.minY + (titleBox.height - tRect.height) / 2
(title as NSString).draw(with: NSRect(x: titleBox.minX, y: ty, width: titleBox.width, height: tRect.height),
                         options: [.usesLineFragmentOrigin], attributes: tAttrs)

// brand footer
let line = NSRect(x: W / 2 - 40, y: 150, width: 80, height: 3)
NSColor(calibratedRed: 0.949, green: 0.722, blue: 0.294, alpha: 1).setFill()
line.fill()
let brand: [NSAttributedString.Key: Any] = [.font: font(["NewYork-Bold", "Georgia-Bold"], 44, bold: true),
                                            .foregroundColor: green, .paragraphStyle: center]
("ourty" as NSString).draw(in: NSRect(x: 0, y: 80, width: W, height: 56), withAttributes: brand)
let sub: [NSAttributedString.Key: Any] = [.font: font(["AvenirNext-Medium", "Avenir-Medium"], 24),
                                          .foregroundColor: muted, .kern: 1.5, .paragraphStyle: center]
("Read the full article  →" as NSString).draw(in: NSRect(x: 0, y: 40, width: W, height: 34), withAttributes: sub)

NSGraphicsContext.restoreGraphicsState()
guard let png = rep.representation(using: .png, properties: [:]) else { exit(1) }
try png.write(to: URL(fileURLWithPath: outPath))
print("saved \(outPath)")
