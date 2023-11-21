permit(
  principal in Bookstore::Role::"Admin",
  action in [ Bookstore::Action::"View" ],
  resource
);

forbid(
  principal == Bookstore::User::"Frank",
  action in [ Bookstore::Action::"View" ],
  resource
);

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

permit (
  principal in Bookstore::Role::"Customer",
  action in [ Bookstore::Action::"ViewPremiumOffers" ],
  resource
)
when {
  principal has yearsAsMember && principal.yearsAsMember >= 2
};

forbid (
  principal in Bookstore::Role::"Customer",
  action in [ Bookstore::Action::"ViewPremiumOffers" ],
  resource
)
when {
  principal has yearsAsMember && principal.yearsAsMember < 2
};

forbid (
  principal,
  action in [ Bookstore::Action::"View", Bookstore::Action::"ViewPremiumOffers" ],
  resource
)
when {
  context.region != "US"
};
