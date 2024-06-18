import express from 'express'
import jose from 'node-jose'
import crypto from 'crypto'
import https from 'https'
import fs from 'fs'
import { time } from 'console';

const app = express();

const key = fs.readFileSync('./key.pem');
const cert = fs.readFileSync('./cert.pem');

// Change these parameters according to your IBM Security Verify tenant
const clientId = "<your_clientid>"
const clientSecret = "<your_clientsecret>"
const authorizationHeader = "Basic " + Buffer.from(`${clientId}:${clientSecret}`).toString('base64')
const tenant = "<your_tenant>" // without protocol

const port = 8080
const introspectEndpoint = `/oauth2/introspect`

let dpopProof = true
let computedFingerprint = ''
let tokenCache = []

app.get("/", (request, response) => {
  response.send("Web app to demonstrate ISV high assurance flows")
})

app.get("/validate-token", async (request, response) => {

  computedFingerprint = ''
  dpopProof = true

  console.log("-------------------------------------------------------------------------------------------")
  const accessToken = request.headers.authorization.split(" ")[1]
  const dpopHeader = request.headers["dpop"]
  // console.log("Access token: " + accessToken)
  // console.log("DPoP header: " + request.headers["dpop"])

  await validateDpopHeader(request, dpopHeader, accessToken)
  
  if (dpopProof) {
    const timeInSec = new Date().getTime() / 1000
    const cachedTokenExp = tokenCache[accessToken]

    if ((cachedTokenExp != undefined) && (timeInSec < cachedTokenExp)) {
      console.log("Token found in cache: %s.", accessToken)
      console.log("Valid until:  %s", new Date(cachedTokenExp * 1000))
      console.log("Current time: %s", new Date(timeInSec * 1000))
    } else {
      const responseText = await doTokenInspectionRequest(accessToken)

      const introspectionResponse = JSON.parse(responseText)
      dpopProof = dpopProof && (introspectionResponse["cnf"]["jkt"] !== undefined)
      dpopProof = dpopProof && (introspectionResponse["cnf"]["jkt"] === computedFingerprint)
      console.log("JWK fingerprint match: " + (introspectionResponse["cnf"]["jkt"] === computedFingerprint))

      if (dpopProof) {
        console.log("Store token %s in cache. Expires at: %s", accessToken, new Date(introspectionResponse["exp"] * 1000))
        tokenCache[accessToken] = introspectionResponse["exp"]
      } else {
        console.log("Remove token %s from cache", accessToken)
        tokenCache[accessToken] = undefined
      }
    }
  }

  console.log("Authorization result: " + dpopProof.toString().toUpperCase())
  console.log("###########################################################################################")
  if (dpopProof) {
    response.sendStatus(204)
  } else {
    response.sendStatus(401)
  }
})

async function doTokenInspectionRequest(accessToken) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: tenant,
      port: 443,
      path: introspectEndpoint,
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': authorizationHeader
      }
    }

    const payload = `token=${accessToken}&token_type_hint=DPoP`

    let responseData = []
    // console.log("Request options: " + JSON.stringify(options))
    // console.log("Request payload: " + payload)

    const request = https.request(options, (response) => {
      response.on('data', chunk => {
        responseData.push(chunk)
      })

      response.on('end', function () {
        const responseBody = Buffer.concat(responseData).toString()
        console.log("Token introspection: " + responseBody)
        resolve(responseBody)
      })
    })

    request.write(payload)

    request.on('error', error => {
      console.log('> Error: ', error.message)
      dpopProof = false
      reject(error)
    })

    request.end();
  })
}

async function validateDpopHeader(request, dpopHeader, accessToken) {

  try {
    dpopProof = dpopProof && (request.headers["dpop"].split(',').length == 1)
    console.log("There is only one DPoP HTTP request header field: " + dpopProof)

    // The DPoP HTTP request header field value is a single and well-formed JWT.
    // The JWT signature verifies with the public key contained in the jwk JOSE Header Parameter
    let dpopHeaderUnpacked = await jose.JWS.createVerify().verify(dpopHeader, { allowEmbeddedKey: true })
    let jsonPayload = JSON.parse(dpopHeaderUnpacked.payload)
    let htu = jsonPayload.htu
    let htm = jsonPayload.htm
    let ath = jsonPayload.ath
    let jti = jsonPayload.jti
    let iat = jsonPayload.iat
    let exp = iat + 60

    // All required claims per Section 4.2 are contained in the JWT.
    dpopProof = dpopProof && (htu !== undefined)
    dpopProof = dpopProof && (htm !== undefined)
    dpopProof = dpopProof && (ath !== undefined)
    dpopProof = dpopProof && (jti !== undefined)
    dpopProof = dpopProof && (iat !== undefined)
    console.log("All required claims per Section 4.2 are contained in the JWT: " + dpopProof)

    // The typ JOSE Header Parameter has the value dpop+jwt.
    dpopProof = dpopProof && (dpopHeaderUnpacked.header.typ === "dpop+jwt")
    console.log("The typ JOSE Header Parameter has the value dpop+jwt: " + (dpopHeaderUnpacked.header.typ === "dpop+jwt"))

    // The alg JOSE Header Parameter indicates a registered asymmetric digital signature algorithm.
    dpopProof = dpopProof && (dpopHeaderUnpacked.header.alg === "RS256")
    console.log("The alg JOSE Header Parameter indicates a registered asymmetric digital signature algorithm: " + (dpopHeaderUnpacked.header.alg === "RS256"))

    console.log("DPoP header payload: " + JSON.stringify(jsonPayload))
    console.log("Url: " + htu)
    console.log("Method DPoP: " + htm)
    console.log("Method request: " + request.method)

    // The htm claim matches the HTTP method of the current request.
    dpopProof = dpopProof && (htm === request.method)
    console.log("The htm claim matches the HTTP method of the current request: " + (htm === request.method))

    // The htu claim matches the HTTP URI value for the HTTP request in which the JWT was received
    const fullUrl = request.protocol + '://' + request.get('host') + request.originalUrl
    dpopProof = dpopProof && (htu === fullUrl)
    console.log("HTU: " + htu)
    console.log("URL: " + fullUrl)
    console.log("The htu claim matches the HTTP URI value for the HTTP request in which the JWT was received: " + (htu === fullUrl))

    // The creation time of the JWT ... is within an acceptable window.
    const timeInSec = new Date().getTime() / 1000
    dpopProof = dpopProof && (iat < timeInSec + 1) && (exp > timeInSec)
    console.log("iat " + new Date(iat * 1000))
    console.log("cts " + new Date((timeInSec + 1) * 1000))
    console.log("exp " + new Date(exp * 1000))
    console.log("The creation time of the JWT ... is within an acceptable window of 60 seconds: " + ((iat < (timeInSec + 1)) && (exp > timeInSec)))

    let digest = crypto.createHash('sha256').update(accessToken).digest()
    let atHash = jose.util.base64url.encode(digest);
    console.log("ath (calculated): " + atHash)
    console.log("ath (from DPoP header): " + ath)

    dpopProof = dpopProof && (atHash === ath)
    console.log("DPoP header is associated with the access token: " + (atHash === ath))

    let thumbprint = await dpopHeaderUnpacked.key.thumbprint('SHA-256');
    computedFingerprint = jose.util.base64url.encode(thumbprint);
    console.log("JWK fingerprint: " + computedFingerprint)

  } catch (error) {
    dpopProof = false
    console.log(error)
  }
}

app.get("/status", (request, response) => {
  const status = {
    "Status": "Running"
  }

  response.send(status)
})

const server = https.createServer({key: key, cert: cert }, app);
server.listen(8080, () => { 
  console.log(`SERVER STARTED ON localhost:${port}`);
})
