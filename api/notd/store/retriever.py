from typing import Optional
from typing import Sequence

from databases import Database
import sqlalchemy

from notd.model import *
from notd.core.exceptions import *
from notd.store.schema import *
from notd.store.schema_conversions import *
from notd.core.exceptions import *

class Retriever:

    def __init__(self, database: Database):
        self.database = database

    # async def get_token_transfer(self, accountId: int) -> Account:
    #     query = AccountsTable.select(AccountsTable.c.id == accountId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'Account {accountId} not found')
    #     account = account_from_row(row)
    #     if account.accountType == 'deleted':
    #         raise BadRequestException(message=f'Account {accountId} has been deleted')
    #     return account

    # async def get_accounts(self, accountIds: Optional[Sequence[int]] = None) -> Sequence[Account]:
    #     query = AccountsTable.select() \
    #         .where(AccountsTable.c.account_type != 'deleted')
    #     if accountIds:
    #         query = query.where(AccountsTable.c.id.in_(accountIds))
    #     rows = await self.database.fetch_all(query=query)
    #     accounts = [account_from_row(row) for row in rows]
    #     return accounts

    # async def get_account_subscription(self, accountSubscriptionId: int) -> AccountSubscription:
    #     query = AccountSubscriptionsTable.select(AccountSubscriptionsTable.c.id == accountSubscriptionId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'AccountSubscription {accountSubscriptionId} not found')
    #     accountSubscription = account_subscription_from_row(row)
    #     return accountSubscription

    # async def get_account_subscription_by_account_id(self, accountId: int) -> AccountSubscription:
    #     query = AccountSubscriptionsTable.select(AccountSubscriptionsTable.c.account_id == accountId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'AccountSubscription with accountId {accountId} not found')
    #     accountSubscription = account_subscription_from_row(row)
    #     return accountSubscription

    # async def get_account_subscription_by_stripe_subscription_id(self, stripeSubscriptionId: int) -> AccountSubscription:
    #     query = AccountSubscriptionsTable.select(AccountSubscriptionsTable.c.stripe_subscription_id == stripeSubscriptionId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'AccountSubscription with stripeSubscriptionId {stripeSubscriptionId} not found')
    #     accountSubscription = account_subscription_from_row(row)
    #     return accountSubscription

    # async def get_site(self, siteId: int) -> Site:
    #     query = SitesTable.select(SitesTable.c.id == siteId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'Site {siteId} not found')
    #     site = site_from_row(row)
    #     return site

    # async def get_site_by_slug(self, slug: str) -> Optional[Site]:
    #     query = SitesTable.select(SitesTable.c.slug == slug)
    #     row = await self.database.fetch_one(query=query)
    #     site = site_from_row(row) if row else None
    #     return site

    # async def list_sites(self, accountId: Optional[int] = None, shouldExcludeArchived: bool = True) -> Sequence[Site]:
    #     query = SitesTable.select()
    #     if accountId is not None:
    #         query = query.where(SitesTable.c.account_id == accountId)
    #     if shouldExcludeArchived:
    #         query = query.where(SitesTable.c.archive_date.is_(None))
    #     rows = await self.database.fetch_all(query=query)
    #     sites = [site_from_row(row) for row in rows]
    #     return sites

    # async def get_site_version(self, siteVersionId: int) -> SiteVersion:
    #     query = SiteVersionsTable.select(SiteVersionsTable.c.id == siteVersionId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'SiteVersion {siteVersionId} not found')
    #     siteVersion = site_version_from_row(row)
    #     return siteVersion

    # async def list_site_versions(self, siteId: int, shouldExcludeArchived: bool = True) -> Sequence[SiteVersion]:
    #     query = SiteVersionsTable.select() \
    #         .where(SiteVersionsTable.c.site_id == siteId)
    #     if shouldExcludeArchived:
    #         query = query.where(SiteVersionsTable.c.archive_date.is_(None))
    #     rows = await self.database.fetch_all(query=query)
    #     siteVersions = [site_version_from_row(row) for row in rows]
    #     return siteVersions

    # async def get_site_primary_version(self, siteId: int) -> SitePrimaryVersion:
    #     query = SitePrimaryVersionsTable.select(SitePrimaryVersionsTable.c.site_id == siteId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'Site Primary Version for site {siteId} not found')
    #     sitePrimaryVersion = site_primary_version_from_row(row)
    #     return sitePrimaryVersion

    # async def get_primary_site_version(self, siteId: int) -> SiteVersion:
    #     sitePrimaryVersion = await self.get_site_primary_version(siteId=siteId)
    #     return await self.get_site_version(siteVersionId=sitePrimaryVersion.siteVersionId)

    # async def get_site_version_entry(self, siteVersionId: int) -> SiteVersionEntry:
    #     query = SiteVersionEntriesTable.select(SiteVersionEntriesTable.c.site_version_id == siteVersionId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'SiteVersionEntry for siteVersion {siteVersionId} not found')
    #     siteVersionEntry = site_version_entry_from_row(row)
    #     return siteVersionEntry

    # async def get_template_category(self, templateCategoryId: int) -> TemplateCategory:
    #     query = TemplateCategoriesTable.select(TemplateCategoriesTable.c.id == templateCategoryId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'TemplateCategory {templateCategoryId} not found')
    #     templateCategory = template_category_from_row(row)
    #     return templateCategory

    # async def list_template_categories(self) -> Sequence[TemplateCategory]:
    #     query = TemplateCategoriesTable.select().order_by(TemplateCategoriesTable.c.id.asc())
    #     rows = await self.database.fetch_all(query=query)
    #     templateCategories = [template_category_from_row(row) for row in rows]
    #     return templateCategories

    # async def get_template(self, templateId: int) -> Template:
    #     query = TemplatesTable.join(SitesTable, TemplatesTable.c.site_id == SitesTable.c.id).select() \
    #         .with_only_columns([TemplatesTable, SitesTable.c.slug]) \
    #         .where(TemplatesTable.c.id == templateId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'Template {templateId} not found')
    #     template = template_from_row(row)
    #     return template

    # async def list_templates(self, templateCategoryId: Optional[int] = None) -> Sequence[Template]:
    #     query = TemplatesTable.join(SitesTable, TemplatesTable.c.site_id == SitesTable.c.id).select() \
    #         .with_only_columns([TemplatesTable, SitesTable.c.slug]) \
    #         .order_by(TemplatesTable.c.id.asc())
    #     if templateCategoryId is not None:
    #         query = query.where(TemplatesTable.c.template_category_id == templateCategoryId)
    #     rows = await self.database.fetch_all(query=query)
    #     templates = [template_from_row(row) for row in rows]
    #     return templates

    # async def get_section_category(self, sectionCategoryId: int) -> SectionCategory:
    #     query = SectionCategoriesTable.select(SectionCategoriesTable.c.id == sectionCategoryId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'SectionCategory {sectionCategoryId} not found')
    #     sectionCategory = section_category_from_row(row)
    #     return sectionCategory

    # async def list_section_categories(self) -> Sequence[SectionCategory]:
    #     query = SectionCategoriesTable.select().order_by(SectionCategoriesTable.c.id.asc())
    #     rows = await self.database.fetch_all(query=query)
    #     sectionCategories = [section_category_from_row(row) for row in rows]
    #     return sectionCategories

    # async def get_section(self, sectionId: int) -> Section:
    #     query = SectionsTable.select().where(SectionsTable.c.id == sectionId)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'Section {sectionId} not found')
    #     section = section_from_row(row)
    #     return section

    # async def get_section_by_type(self, sectionType: str) -> Section:
    #     query = SectionsTable.select().where(SectionsTable.c.type == sectionType)
    #     row = await self.database.fetch_one(query=query)
    #     if not row:
    #         raise NotFoundException(message=f'Section with type {sectionType} not found')
    #     section = section_from_row(row)
    #     return section

    # async def list_sections(self, sectionCategoryId: Optional[int] = None) -> Sequence[Section]:
    #     query = SectionsTable.select().order_by(SectionsTable.c.id.asc())
    #     if sectionCategoryId is not None:
    #         query = query.where(SectionsTable.c.section_category_id == sectionCategoryId)
    #     rows = await self.database.fetch_all(query=query)
    #     sections = [section_from_row(row) for row in rows]
    #     return sections
