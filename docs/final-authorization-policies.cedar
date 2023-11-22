// Scenario 1: Scenario 1: Admin Access (RBAC)

permit (
  principal in Bookstore::Role::"Admin",
  action in [ Bookstore::Action::"View" ],
  resource
);

// Scenario 2: Explicit Deny for Admin User 'Frank' (RBAC)

forbid (
  principal == Bookstore::User::"Frank",
  action in [ Bookstore::Action::"View" ],
  resource
);

// Scenario 3: Regional Restriction (Context-Based Access Control)

forbid (
  principal,
  action in [ Bookstore::Action::"View", Bookstore::Action::"ViewWithPremiumOffers" ],
  resource
)
when {
  context.region != "US"
};

// Scenario 4: Loyal Customer Access to Premium Offers (ABAC)

permit (
  principal in Bookstore::Role::"Customer",
  action in [ Bookstore::Action::"ViewWithPremiumOffers" ],
  resource
)
when {
  principal has yearsAsMember && principal.yearsAsMember >= 2
};

forbid (
  principal in Bookstore::Role::"Customer",
  action in [ Bookstore::Action::"ViewWithPremiumOffers" ],
  resource
)
when {
  principal has yearsAsMember && principal.yearsAsMember < 2
};

// Scenario 5: Publisher Resource Owner - Users Dante and William (Bulk Authorization)

permit (
  principal in Bookstore::Role::"Publisher",
  action in [ Bookstore::Action::"View" ],
  resource
)
when {
  principal == resource.owner
};

permit (
  //
  // Ideally, in production cases you should have here immutable identifiers.
  // According to the best practices, you should avoid mutable identifiers - like username:
  //
  //   https://docs.cedarpolicy.com/bestpractices/bp-mutable-identifiers.html
  //
  principal == Bookstore::User::"Dante",
  action in [ Bookstore::Action::"View" ],
  resource == Bookstore::Book::"em1oadaa-b22k-4ea8-kk33-f6m217604o3m"
);
