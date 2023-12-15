//
// Copyright contributors to the IBM Security Verify DPoP Sample App for iOS project
//

import Foundation
import Authentication
import Core

@Observable class ViewModel {
    var resourceServer = "https://localhost:8080/validate-token"
    var tokenURL = "https://verify.ibm.com/oauth2/token"
    var clientId = "x1y2z3"
    var clientSecret = "a1b2c3"
    var token: TokenInfo? = nil
    var error: Error? = nil
    
    private let key = RSA.Signing.PrivateKey()
    
    public func requestToken() async {
        do {
            let parameters: [String: Any] = ["grant_type": "client_credentials",
                                             "client_id": "\(clientId)",
                                             "client_secret": "\(clientSecret)"]
            
            let body = urlEncode(from: parameters).data(using: .utf8)!
            
            // Generate the request for a DPoP access token
            let tokenResource = HTTPResource<TokenInfo>(json: .post,
                                                        url: URL(string: tokenURL)!,
                                                        contentType: .urlEncoded,
                                                        body: body,
                                                        headers: ["DPoP": try DPoP.generateProof(key, uri: tokenURL)],
                                                        timeOutInterval: 30)
            
            self.token = try await URLSession(configuration: .default).dataTask(for: tokenResource)
            print("Succesfully request an access token with a DPoP header.")
        }
        catch let error {
            self.error = error
        }
    }
    
    public func validateToken() async {
        self.error = nil
        guard let token = self.token else {
            self.error = OAuthProviderError.general(message: "No token to validate.")
            return
        }
        
        do {
            // Generate the JWT to validate the DPoP against the intraspection resource.
            let validationResource = HTTPResource<()>(.get,
                                                      url: URL(string: resourceServer)!,
                                                      headers: ["DPoP": try DPoP.generateProof(key, uri: resourceServer, method: .get, accessToken: token.accessToken),
                                                                "Authorization": "\(token.tokenType) \(token.accessToken)"],
                                                      timeOutInterval: 30)
            
            try await URLSession(configuration: .default, delegate: SelfSignedCertificateDelegate(), delegateQueue: nil).dataTask(for: validationResource)
            print("Succesfully validated the access token with a DPoP header against \(resourceServer).")
        }
        catch let error {
            self.error = error
        }
    }
}
