# 0013-renaming-cluster-hostnames-to-mik-mak-muk

* **Status:** Accepted
* **Date:** 2026-08-10

**Context**

The cluster hostnames were originally set to *kwik*, *kwak*, and *kwek* (the Dutch names for Huey, Dewey, and Louie). While recognizable in the Netherlands, these names carry two distinct drawbacks:

* **International Relevance:** Dutch names are meaningless and hard to pronounce or recognize for an international technical audience.
* **Legal and Trademark Concerns:** Huey, Dewey, and Louie are copyrighted characters owned by The Walt Disney Company. Disney character names vary significantly across languages—for example, Donald Duck is known as *Anders And* in Denmark and Norway. Relying on regionally specific copyrighted names introduces unwanted corporate licensing ambiguity and trademark issues.

To ensure safety across multiple languages, a verification step was conducted to confirm that **mik**, **mak**, and **muk** carry no obscene, offensive, or inappropriate meanings in common international languages.

*(Note: This record is intentionally designated as ADR **0013** as a nod to 313, the famous license plate number of Donald Duck's car.)*

**Decision**

Rename all cluster nodes from *kwik*, *kwak*, and *kwek* to **mik**, **mak**, and **muk**.

**Consequences**

* **Positive:** Eliminates potential Disney trademark risks and removes local Dutch language dependencies for international readability.
* **Positive:** Uses a clean, short, and universally readable naming scheme.
* **Cultural & Linguistic Context:**
* **Dutch Expression:** Provides a fun local reference to the Dutch idiom *"met de hele mikmak"* (meaning "the whole shebang" or "everything included").
* **Gaelic / Irish Reference:** In Irish (Gaelic), **muck** (spelled *muc*) simply means "pig" or "swine," remaining completely neutral and benign.
* **Slavic / Ukrainian Reference:** In Ukrainian and broader Slavic languages, **mak** (мак) translates to "poppy," providing an innocent everyday word.


* **Negative:** Requires updating local SSH configurations, inventory files, static DNS records, and Ansible playbooks to reference the new hostnames.
