package com.ibm.security.verify.dpop

import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.HeaderMap
import retrofit2.http.Headers
import retrofit2.http.POST
import retrofit2.http.Url

interface ApiService {

    @POST
    @FormUrlEncoded
    @Headers("Accept: application/json")
    fun requestDpopToken(
        @HeaderMap headers: HashMap<String, String>,
        @Url url: String?,
        @Field("client_id") clientId: String?,
        @Field("client_secret") username: String?,
        @Field("grant_type") grantType: String?,
        @Field("scope") scope: String?
    ): Call<DpopToken>

    @GET
    @Headers("Accept: application/json")
    fun validateDpopToken(
        @HeaderMap headers: HashMap<String, String>,
        @Header("Authorization") token: String?,
        @Url url: String?
    ): Call<ResponseBody>

}