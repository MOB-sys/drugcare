import google_mobile_ads
import GoogleMobileAds
import UIKit

class ListTileNativeAdFactory: NSObject, FLTNativeAdFactory {
  func createNativeAd(
    _ nativeAd: GADNativeAd,
    customOptions: [AnyHashable: Any]?
  ) -> GADNativeAdView? {
    let nativeAdView = GADNativeAdView()

    let headlineLabel = UILabel()
    headlineLabel.font = .systemFont(ofSize: 16, weight: .bold)
    headlineLabel.numberOfLines = 1
    headlineLabel.text = nativeAd.headline
    headlineLabel.translatesAutoresizingMaskIntoConstraints = false

    let bodyLabel = UILabel()
    bodyLabel.font = .systemFont(ofSize: 14)
    bodyLabel.numberOfLines = 2
    bodyLabel.textColor = .gray
    bodyLabel.text = nativeAd.body
    bodyLabel.translatesAutoresizingMaskIntoConstraints = false

    nativeAdView.addSubview(headlineLabel)
    nativeAdView.addSubview(bodyLabel)

    nativeAdView.headlineView = headlineLabel
    nativeAdView.bodyView = bodyLabel

    NSLayoutConstraint.activate([
      headlineLabel.leadingAnchor.constraint(equalTo: nativeAdView.leadingAnchor, constant: 8),
      headlineLabel.trailingAnchor.constraint(equalTo: nativeAdView.trailingAnchor, constant: -8),
      headlineLabel.topAnchor.constraint(equalTo: nativeAdView.topAnchor, constant: 8),
      bodyLabel.leadingAnchor.constraint(equalTo: nativeAdView.leadingAnchor, constant: 8),
      bodyLabel.trailingAnchor.constraint(equalTo: nativeAdView.trailingAnchor, constant: -8),
      bodyLabel.topAnchor.constraint(equalTo: headlineLabel.bottomAnchor, constant: 4),
      bodyLabel.bottomAnchor.constraint(equalTo: nativeAdView.bottomAnchor, constant: -8),
    ])

    nativeAdView.nativeAd = nativeAd
    return nativeAdView
  }
}
