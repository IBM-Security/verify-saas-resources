//
// Copyright contributors to the IBM Security Verify DPoP Sample App for iOS project
//

import SwiftUI

struct ContentView: View {
    @State private var viewModel = ViewModel()
    
    var body: some View {
        NavigationView {
        VStack(spacing: 16) {
            Spacer()
            Image(systemName: "person.circle")
                .resizable()
                .frame(width: 50, height: 50)
                .foregroundColor(.blue)
            
                VStack(spacing: 8) {
                    Text("This sample app demonstrates initiating an DPoP to generate an access token and validate against an external resource.")
                        .foregroundColor(.secondary)
                        .font(.title2)
                        .multilineTextAlignment(.center)
                        .padding()
                    
                    ScrollViewReader {_ in
                        Form {
                            Section(header: Text("Resource Endpoint")) {
                                TextField(text: $viewModel.resourceServer, prompt: Text("Resource URL")) {
                                        Text("The URL to the resource endpoint.")
                                }
                            }
                            Section(header: Text("Token Endpoint")) {
                                TextField(text: $viewModel.tokenURL, prompt: Text("Token URL")) {
                                        Text("The URL to the token endpoint.")
                                }
                            }
                            Section(header: Text("Client ID")) {
                                TextField(text: $viewModel.clientId, prompt: Text("Client ID")) {
                                        Text("The client identifier.")
                                }
                            }
                            Section(header: Text("Client Secret")) {
                                TextField(text: $viewModel.clientSecret, prompt: Text("Client Secret")) {
                                        Text("The client secret.")
                                }
                            }
                           
                        }.padding()
                        .cornerRadius(16)
                    }
                    
                    HStack {
                        VStack {
                            Button {
                                Task {
                                    await viewModel.requestToken()
                                }
                            } label: {
                                Text("Request DPoP Token")
                                    .frame(maxWidth:.infinity)
                                    .foregroundColor(.white)
                                    .padding()
                                    .background(viewModel.token == nil ? .blue : .gray)
                                    .cornerRadius(8)
                            }
                            .disabled(viewModel.token != nil)
                            
                            Button {
                                Task {
                                    await viewModel.validateToken()
                                }
                            } label: {
                                Text("Validate DPoP Token")
                                    .frame(maxWidth:.infinity)
                                    .foregroundColor(.white)
                                    .padding()
                                    .background(viewModel.token != nil ? .blue : .gray)
                                    .cornerRadius(8)
                            }
                            .disabled(viewModel.token == nil)
                        }
                    }
                    .frame(maxWidth:.infinity)
                    .padding(16)
                    .alert(viewModel.error?.localizedDescription ?? "", isPresented: .constant(viewModel.error != nil)) {
                        Button("OK") { }
                    }
                }
            }
        }
    }
}

#Preview {
    ContentView()
}
