import datetime
from typing import Dict
from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import Json

from notd.model import Token
from notd.model import TokenTransfer
from notd.model import UiData

class ApiTokenTransfer(BaseModel):
    tokenTransferId: int
    transactionHash: str
    registryAddress: str
    fromAddress: str
    toAddress: str
    tokenId: str
    value: int
    gasLimit: int
    gasPrice: int
    gasUsed: int
    blockNumber: int
    blockHash: str
    blockDate: datetime.datetime

    @classmethod
    def from_model(cls, model: UiData):
        return cls(
            tokenTransferId=model.tokenTransferId,
            transactionHash=model.transactionHash,
            registryAddress=model.registryAddress,
            fromAddress=model.fromAddress,
            toAddress=model.toAddress,
            tokenId=model.tokenId,
            value=model.value,
            gasLimit=model.gasLimit,
            gasPrice=model.gasPrice,
            gasUsed=model.gasUsed,
            blockNumber=model.blockNumber,
            blockHash=model.blockHash,
            blockDate=model.blockDate,
        )

class ApiToken(BaseModel):
    registryAddress: str
    tokenId: str

    @classmethod
    def from_model(cls, model: UiData):
        return cls(
            registryAddress=model.registryAddress,
            tokenId=model.tokenId,
        )

class ApiUiData(BaseModel):
    highestPricedTokenTransfer: ApiTokenTransfer
    mostTradedTokenTransfers: List[ApiTokenTransfer]
    randomTokenTransfer: ApiTokenTransfer
    sponsoredToken: ApiToken

    @classmethod
    def from_model(cls, model: UiData):
        return cls(
            highestPricedTokenTransfer=ApiTokenTransfer.from_model(model=model.highestPricedTokenTransfer),
            mostTradedTokenTransfers=[ApiTokenTransfer.from_model(model=transfer) for transfer in model.mostTradedTokenTransfers],
            randomTokenTransfer=ApiTokenTransfer.from_model(model=model.randomTokenTransfer),
            sponsoredToken=ApiToken.from_model(model=model.sponsoredToken),
        )

# class ApiStripeSubscription(BaseModel):
#     subscriptionId: str
#     status: str
#     latestInvoicePaymentStatus: Optional[str]
#     latestInvoicePaymentActionSecret: Optional[str]

#     @classmethod
#     def from_model(cls, model: StripeSubscription):
#         return cls(
#             subscriptionId=model.subscriptionId,
#             status=model.status,
#             latestInvoicePaymentStatus=model.latestInvoicePaymentStatus,
#             latestInvoicePaymentActionSecret=model.latestInvoicePaymentActionSecret,
#         )

# class ApiStripePortalSession(BaseModel):
#     portalSessionId: str
#     url: str

#     @classmethod
#     def from_model(cls, model: StripePortalSession):
#         return cls(
#             portalSessionId=model.portalSessionId,
#             url=model.url,
#         )

# class ApiSite(BaseModel):
#     siteId: int
#     accountId: int
#     slug: str
#     name: str
#     isPublishing: bool
#     archiveDate: Optional[datetime.datetime]
#     customDomain: Optional[str]
#     customDomainStatus: Optional[str]

#     @classmethod
#     def from_site(cls, site: Site):
#         return cls(
#             siteId=site.siteId,
#             accountId=site.accountId,
#             slug=site.slug,
#             name=site.name,
#             isPublishing=site.isPublishing,
#             archiveDate=site.archiveDate,
#             customDomain=site.customDomain,
#             customDomainStatus=site.customDomainStatus,
#         )

# class ApiSiteVersion(BaseModel):
#     siteVersionId: int
#     creationDate: datetime.datetime
#     siteId: int
#     buildHash: str
#     name: Optional[str]
#     isPublishing: bool
#     publishDate: Optional[datetime.datetime]
#     archiveDate: Optional[datetime.datetime]
#     lastUpdateDate: datetime.datetime

#     @classmethod
#     def from_site_version(cls, siteVersion: SiteVersion):
#         return cls(
#             siteVersionId=siteVersion.siteVersionId,
#             creationDate=siteVersion.creationDate,
#             siteId=siteVersion.siteId,
#             buildHash=siteVersion.buildHash,
#             name=siteVersion.name,
#             isPublishing=siteVersion.isPublishing,
#             publishDate=siteVersion.publishDate,
#             archiveDate=siteVersion.archiveDate,
#             lastUpdateDate=siteVersion.lastUpdateDate,
#         )

# class ApiPresignedUpload(BaseModel):
#     url: str
#     params: Dict[str, str]

#     @classmethod
#     def from_presigned_upload(cls, presignedUpload: S3PresignedUpload):
#         return cls(
#             url=presignedUpload.url,
#             params={field.name: field.value for field in presignedUpload.fields},
#         )

# class ApiAssetFile(BaseModel):
#     path: str

#     @classmethod
#     def from_file(cls, s3File: S3File):
#         return cls(
#             path=s3File.path,
#         )

# class ApiSiteVersionEntry(BaseModel):
#     siteVersionEntryId: int
#     siteVersionId: int
#     siteContent: Dict
#     siteTheme: Dict

#     @classmethod
#     def from_site_version_entry(cls, siteVersionEntry: SiteVersionEntry):
#         return cls(
#             siteVersionEntryId=siteVersionEntry.siteVersionEntryId,
#             siteVersionId=siteVersionEntry.siteVersionId,
#             siteContent=site_util.order_site_content(siteContent=siteVersionEntry.siteContent),
#             siteTheme=site_util.order_site_theme(siteTheme=siteVersionEntry.siteTheme),
#         )

# class ApiTemplateCategory(BaseModel):
#     templateCategoryId: int
#     name: str

#     @classmethod
#     def from_model(cls, model: TemplateCategory):
#         return cls(
#             templateCategoryId=model.templateCategoryId,
#             name=model.name,
#         )

# class ApiTemplate(BaseModel):
#     templateId: int
#     name: str
#     description: str
#     siteId: int
#     templateCategoryId: int
#     previewUrl: str
#     imageUrl: str

#     @classmethod
#     def from_model(cls, model: Template):
#         return cls(
#             templateId=model.templateId,
#             name=model.name,
#             description=model.description,
#             siteId=model.siteId,
#             templateCategoryId=model.templateCategoryId,
#             previewUrl=model.previewUrl,
#             imageUrl=model.imageUrl,
#         )

# class ApiSectionCategory(BaseModel):
#     sectionCategoryId: int
#     name: str

#     @classmethod
#     def from_model(cls, model: SectionCategory):
#         return cls(
#             sectionCategoryId=model.sectionCategoryId,
#             name=model.name,
#         )

# class ApiSection(BaseModel):
#     sectionId: int
#     name: str
#     sectionType: str
#     description: str
#     sectionCategoryId: int
#     previewImageUrl: str
#     content: Dict

#     @classmethod
#     def from_model(cls, model: Section):
#         return cls(
#             sectionId=model.sectionId,
#             name=model.name,
#             sectionType=model.sectionType,
#             description=model.description,
#             sectionCategoryId=model.sectionCategoryId,
#             previewImageUrl=model.previewImageUrl,
#             content=model.content,
#         )

# class ApiIosApp(BaseModel):
#     iosAppId: str
#     name: str
#     description: str
#     publisherName: str
#     iconImageUrl: str
#     storeUrl: str

#     @classmethod
#     def from_ios_app(cls, iosApp: IosApp):
#         return cls(
#             iosAppId=iosApp.iosAppId,
#             name=iosApp.name,
#             description=iosApp.description,
#             publisherName=iosApp.publisherName,
#             iconImageUrl=iosApp.iconImageUrl,
#             storeUrl=iosApp.storeUrl,
#         )

# class ApiAndroidApp(BaseModel):
#     androidAppId: str
#     name: str
#     tagline: str
#     description: str
#     publisherName: str
#     iconImageUrl: str
#     storeUrl: str

#     @classmethod
#     def from_android_app(cls, androidApp: AndroidApp):
#         return cls(
#             androidAppId=androidApp.androidAppId,
#             name=androidApp.name,
#             tagline=androidApp.tagline,
#             description=androidApp.description,
#             publisherName=androidApp.publisherName,
#             iconImageUrl=androidApp.iconImageUrl,
#             storeUrl=androidApp.storeUrl,
#         )

# class LoginUserRequest(BaseModel):
#     email: str
#     password: str

# class LoginUserResponse(BaseModel):
#     pass

# class LogoutUserRequest(BaseModel):
#     pass

# class LogoutUserResponse(BaseModel):
#     pass

# class CreateUserRequest(BaseModel):
#     firstName: str
#     lastName: str
#     email: str
#     password: str
#     shouldJoinNewsletter: Optional[bool]

# class CreateUserResponse(BaseModel):
#     pass

# class RefreshTokenForUserRequest(BaseModel):
#     pass

# class RefreshTokenForUserResponse(BaseModel):
#     pass

# class SendEmailVerificationForUserRequest(BaseModel):
#     pass

# class SendEmailVerificationForUserResponse(BaseModel):
#     pass

# class RetrieveAccountsRequest(BaseModel):
#     pass

# class RetrieveAccountsResponse(BaseModel):
#     accounts: List[ApiAccount]

# # class CreateAccountRequest(BaseModel):
# #     name: str

# # class CreateAccountResponse(BaseModel):
# #     account: ApiAccount

# class GetAccountRequest(BaseModel):
#     pass

# class GetAccountResponse(BaseModel):
#     account: ApiAccount

# class RetrieveSitesForAccountRequest(BaseModel):
#     pass

# class RetrieveSitesForAccountResponse(BaseModel):
#     sites: List[ApiSite]

# class CreateSubscriptionForAccountRequest(BaseModel):
#     planCode: str
#     priceCode: str
#     stripePaymentMethodId: str
#     couponCode: Optional[str]

# class CreateSubscriptionForAccountResponse(BaseModel):
#     stripeSubscription: ApiStripeSubscription

# class ChangeSubscriptionForAccountRequest(BaseModel):
#     planCode: str
#     priceCode: str
#     couponCode: Optional[str]

# class ChangeSubscriptionForAccountResponse(BaseModel):
#     stripeSubscription: ApiStripeSubscription

# class CreatePortalSessionForAccountRequest(BaseModel):
#     pass

# class CreatePortalSessionForAccountResponse(BaseModel):
#     stripePortalSession: ApiStripePortalSession

# class CreateSiteForAccountRequest(BaseModel):
#     slug: str
#     name: Optional[str]
#     templateId: Optional[int]

# class CreateSiteForAccountResponse(BaseModel):
#     site: ApiSite

# class CreateSiteVersionRequest(BaseModel):
#     siteContent: Optional[Dict]
#     siteTheme: Optional[Dict]
#     name: Optional[str]
#     templateId: Optional[str]

# class CreateSiteVersionResponse(BaseModel):
#     siteVersion: ApiSiteVersion

# class RetrieveNextVersionNameRequest(BaseModel):
#     pass

# class RetrieveNextVersionNameResponse(BaseModel):
#     nextVersionName: str

# class GetSiteVersionRequest(BaseModel):
#     pass

# class GetSiteVersionResponse(BaseModel):
#     siteVersion: ApiSiteVersion

# class ListSiteVersionAssetsRequest(BaseModel):
#     pass

# class ListSiteVersionAssetsResponse(BaseModel):
#     assetFiles: List[ApiAssetFile]

# class DeleteSiteVersionAssetsRequest(BaseModel):
#     pass

# class DeleteSiteVersionAssetsResponse(BaseModel):
#     pass

# class PromoteSiteVersionRequest(BaseModel):
#     pass

# class PromoteSiteVersionResponse(BaseModel):
#     pass

# class CloneSiteVersionRequest(BaseModel):
#     name: Optional[str]

# class CloneSiteVersionResponse(BaseModel):
#     siteVersion: ApiSiteVersion

# class ArchiveSiteVersionRequest(BaseModel):
#     pass

# class ArchiveSiteVersionResponse(BaseModel):
#     siteVersion: ApiSiteVersion

# class GenerateAssetUploadForSiteVersionRequest(BaseModel):
#     pass

# class GenerateAssetUploadForSiteVersionResponse(BaseModel):
#     presignedUpload: ApiPresignedUpload

# class GetSiteRequest(BaseModel):
#     pass

# class GetSiteResponse(BaseModel):
#     site: ApiSite

# class UpdateDomainForSiteRequest(BaseModel):
#     customDomain: str

# class UpdateDomainForSiteResponse(BaseModel):
#     site: ApiSite

# class ArchiveSiteRequest(BaseModel):
#     pass

# class ArchiveSiteResponse(BaseModel):
#     site: ApiSite

# class GetSiteBySlugRequest(BaseModel):
#     pass

# class GetSiteBySlugResponse(BaseModel):
#     site: ApiSite

# class ListSiteVersionsRequest(BaseModel):
#     pass

# class ListSiteVersionsResponse(BaseModel):
#     siteVersions: List[ApiSiteVersion]

# class GetSitePrimaryVersionRequest(BaseModel):
#     pass

# class GetSitePrimaryVersionResponse(BaseModel):
#     siteVersion: ApiSiteVersion

# class GetSiteVersionEntryRequest(BaseModel):
#     pass

# class GetSiteVersionEntryResponse(BaseModel):
#     siteVersionEntry: ApiSiteVersionEntry

# class UpdateSiteVersionEntryRequest(BaseModel):
#     siteContent: Optional[Dict]
#     siteTheme: Optional[Dict]

# class UpdateSiteVersionEntryResponse(BaseModel):
#     siteVersionEntry: ApiSiteVersionEntry

# class ListTemplateCategoriesRequest(BaseModel):
#     pass

# class ListTemplateCategoriesResponse(BaseModel):
#     templateCategories: Sequence[ApiTemplateCategory]

# class CreateTemplateCategoryRequest(BaseModel):
#     name: str

# class CreateTemplateCategoryResponse(BaseModel):
#     templateCategory: ApiTemplateCategory

# class GetTemplateCategoryRequest(BaseModel):
#     pass

# class GetTemplateCategoryResponse(BaseModel):
#     templateCategory: ApiTemplateCategory

# class ListTemplatesRequest(BaseModel):
#     pass

# class ListTemplatesResponse(BaseModel):
#     templates: Sequence[ApiTemplate]

# class CreateTemplateRequest(BaseModel):
#     name: str
#     description: str
#     siteId: int
#     templateCategoryId: int

# class CreateTemplateResponse(BaseModel):
#     template: ApiTemplate

# class GetTemplateRequest(BaseModel):
#     pass

# class GetTemplateResponse(BaseModel):
#     template: ApiTemplate

# class GetSiteVersionEntryForTemplateRequest(BaseModel):
#     pass

# class GetSiteVersionEntryForTemplateResponse(BaseModel):
#     siteVersionEntry: ApiSiteVersionEntry

# class ListSectionCategoriesRequest(BaseModel):
#     pass

# class ListSectionCategoriesResponse(BaseModel):
#     sectionCategories: Sequence[ApiSectionCategory]

# class CreateSectionCategoryRequest(BaseModel):
#     name: str

# class CreateSectionCategoryResponse(BaseModel):
#     sectionCategory: ApiSectionCategory

# class GetSectionCategoryRequest(BaseModel):
#     pass

# class GetSectionCategoryResponse(BaseModel):
#     sectionCategory: ApiSectionCategory

# class ListSectionsRequest(BaseModel):
#     pass

# class ListSectionsResponse(BaseModel):
#     sections: Sequence[ApiSection]

# class CreateSectionRequest(BaseModel):
#     name: str
#     sectionType: str
#     description: str
#     sectionCategoryId: int
#     previewImageUrl: str
#     content: Dict

# class CreateSectionResponse(BaseModel):
#     section: ApiSection

# class GetSectionRequest(BaseModel):
#     pass

# class GetSectionResponse(BaseModel):
#     section: ApiSection

# class GetIosAppRequest(BaseModel):
#     pass

# class GetIosAppResponse(BaseModel):
#     iosApp: ApiIosApp

# class GetAndroidAppRequest(BaseModel):
#     pass

# class GetAndroidAppResponse(BaseModel):
#     androidApp: ApiAndroidApp

class RetrieveUiDataRequest(BaseModel):
    # startDate: Optional[datetime.datetime]
    # endDate: Optional[datetime.datetime]
    pass

class RetrieveUiDataResponse(BaseModel):
    uiData: ApiUiData
