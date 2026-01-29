Feature: Task management via HTTP API

  Scenario: Healthcheck returns ok
    When I GET "/health"
    Then Response status is "200"
    And Response JSON has key "status" with value "ok"

  # create + list visibility
  Scenario: Owner sees only own tasks
    Given User "owner-a" with role "USER" exists
    And User "other-a" with role "USER" exists
    And Task list for actor "owner-a" is empty
    When Actor "owner-a" creates a task titled "Task-A"
    And Actor "owner-a" creates a task titled "Task-B"
    Then Actor "owner-a" sees last task in list
    And Actor "other-a" does not see last task in list

  # update + delete
  Scenario: Update and soft-delete hides task from list
    Given User "owner-b" with role "USER" exists
    And Task list for actor "owner-b" is empty
    When Actor "owner-b" creates a task titled "Old"
    And Actor "owner-b" updates the task title to "New" and priority to "HIGH"
    Then Last response status is "200"
    And Last response JSON has key "priority" with value "HIGH"
    When Actor "owner-b" deletes the task
    Then Task is hidden from list for actor "owner-b"

  # assign + events
  Scenario: Manager assigns task and events contain ASSIGNED
    Given User "mgr-1" with role "MANAGER" exists
    And User "dev-1" with role "USER" exists
    And Task list for actor "mgr-1" is empty
    When Actor "mgr-1" creates a task titled "Feature-1"
    And Actor "mgr-1" assigns the task to "dev-1"
    Then Events for the task seen by "mgr-1" include "ASSIGNED"

  # status happy path
  Scenario: Assignee moves task IN_PROGRESS -> DONE and events recorded
    Given User "own-1" with role "USER" exists
    And User "dev-2" with role "USER" exists
    And Task list for actor "own-1" is empty
    When Actor "own-1" creates a task titled "Impl"
    And Actor "own-1" assigns the task to "dev-2"
    And Actor "dev-2" changes status to "IN_PROGRESS"
    And Actor "dev-2" changes status to "DONE"
    Then Events for the task seen by "dev-2" contain "STATUS_CHANGED" exactly "2" times

  # validation / errors
  Scenario: Unknown status returns 400
    Given User "u-x" with role "USER" exists
    And Task list for actor "u-x" is empty
    When Actor "u-x" creates a task titled "X"
    And Actor "u-x" tries to change status to "WHAT_IS_THIS"
    Then Last response status is "400"
    And Last response JSON message contains "Unknown status"

  Scenario: Forbidden assign returns 403
    Given User "own-2" with role "USER" exists
    And User "other-2" with role "USER" exists
    And User "target-2" with role "USER" exists
    And Task list for actor "own-2" is empty
    When Actor "own-2" creates a task titled "Secret"
    And Actor "other-2" tries to assign the task to "target-2"
    Then Last response status is "403"
    And Last response JSON message contains "User cannot assign this task"